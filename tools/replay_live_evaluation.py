#!/usr/bin/env python3
"""Check the published 120-case experiment and recompute its key results."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
from statistics import fmean
import sys


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "paper120_live"
ENGINE = ROOT / "genai_engine"
FROZEN = ENGINE / "targeted_evaluation_repair" / "evaluation_rerun"
MODELS = ("mistral_7b", "qwen2_5_7b", "qwen3_8b")
CASE_CONTROLS = (
    "role", "age_group_code", "stage_id", "channel", "variant",
    "difficulty_band", "language_mode", "retrieval_mode",
)
REPLAYED_SCORES = (
    "json_validity", "game_schema_completeness", "schema_completeness",
    "control_adherence", "common_case_concept_precision", "common_case_concept_recall",
    "common_case_concept_f1", "grounding_completeness", "contradiction",
    "ontology_semantic_scope",
)

sys.path.insert(0, str(ENGINE))
from three_layer_evaluation.io import load_jsonl_records
from three_layer_evaluation.models import METHOD_ORDER
from three_layer_evaluation.scenario_checks import score_record


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_number(value: float, archived: str, label: str) -> None:
    if not math.isclose(value, float(archived), rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"{label}: replayed {value}, archived {archived}")


def lexical_scores(counts: dict[str, int]) -> tuple[float, float, float]:
    generated, matched_generated = counts["generated"], counts["matched_generated"]
    required, matched_required = counts["required"], counts["matched_required"]
    if not (0 <= matched_generated <= generated and 0 <= matched_required <= required):
        raise ValueError(f"invalid lexical audit counts: {counts}")
    precision = matched_generated / max(1, generated)
    recall = matched_required / max(1, required)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def main() -> None:
    manifest = read_json(ARCHIVE / "manifest.json")
    original = read_json(FROZEN / "run_manifest.json")
    original_hashes = {
        path.replace("\\", "/").rsplit("/", 1)[-1]: digest
        for path, digest in original["input_sha256"].items()
    }
    cases_path = ROOT / manifest["frozen_case_manifest"]
    ontology_path = ROOT / manifest["ontology"]
    if sha256(cases_path) != manifest["frozen_case_manifest_sha256"]:
        raise ValueError("frozen case manifest checksum mismatch")
    ontology_hash = sha256(ontology_path)
    if original_hashes[ontology_path.name] != manifest["ontology_sha256"]:
        raise ValueError("original ontology checksums do not match")
    if ontology_hash != manifest.get("public_ontology_sha256", manifest["ontology_sha256"]):
        raise ValueError("public ontology checksum mismatch")

    cases = {row["case_id"]: row for row in read_json(cases_path)["cases"]}
    if len(cases) != 120:
        raise ValueError("expected 120 unique cases")
    components = read_csv(FROZEN / "component_metrics_by_output.csv")
    archived = {(row["case_id"], row["model_key"], row["method"]): row for row in components}
    expected_keys = set(itertools.product(cases, MODELS, METHOD_ORDER))
    if len(components) != len(expected_keys) or archived.keys() != expected_keys:
        raise ValueError("archived component table differs from the 120 x 3 x 4 design")
    files = manifest["files"]
    if len(files) != 12 or {(item["model"], item["mode"]) for item in files} != set(itertools.product(MODELS, METHOD_ORDER)):
        raise ValueError("expected one scenario file per model and mode")

    seen = set()
    f1_by_method = {method: [] for method in METHOD_ORDER}
    oci_by_method = {method: [] for method in METHOD_ORDER}
    gate_accepts = schema_repairs = 0
    for item in files:
        path = ARCHIVE / item["path"]
        if sha256(path) != item["public_sha256"] or original_hashes[path.name] != item["original_sha256"]:
            raise ValueError(f"checksum mismatch: {path.name}")
        records = load_jsonl_records([path], dedupe=False)
        if len(records) != item["records"] or len(records) != len(cases):
            raise ValueError(f"expected 120 rows: {path.name}")
        for record in records:
            row = record.raw
            if record.parse_error or row.get("used_live_llm") is not True or row.get("used_fallback") is not False:
                raise ValueError(f"expected a finalized live-call record: {path.name}:{record.line_number}")
            case = row["case"]
            score = score_record(record)
            key = (case["case_id"], score.model_key, score.method)
            if key in seen or key[1:] != (item["model"], item["mode"]):
                raise ValueError(f"duplicated or misplaced row: {key}")
            seen.add(key)
            if any(case[field] != cases[key[0]][field] for field in CASE_CONTROLS):
                raise ValueError(f"case controls differ from frozen input: {key}")
            original_row = archived[key]
            if score.scenario_id != original_row["scenario_id"]:
                raise ValueError(f"scenario identifier mismatch: {key}")
            for field in REPLAYED_SCORES:
                check_number(getattr(score, field), original_row[field], f"{key} {field}")
            for field in ("automated_decision", "generation_integrity_status"):
                if getattr(score, field) != original_row[field]:
                    raise ValueError(f"{field} mismatch: {key}")
            precision, recall, f1 = lexical_scores(row["paper_lexical_counts"])
            for field, value in (("precision", precision), ("recall", recall), ("f1", f1)):
                check_number(value, original_row[f"required_concept_{field}"], f"{key} lexical {field}")
            oci = 0.20 * (score.json_validity + score.control_adherence + f1
                          + score.grounding_completeness + 1 - score.contradiction)
            check_number(oci, original_row["oci_equal_weight"], f"{key} equal-weight OCI")
            f1_by_method[score.method].append(f1)
            oci_by_method[score.method].append(oci)
            gate_accepts += score.automated_decision == "ACCEPTED"
            schema_repairs += score.schema_safe_repair_used
    if seen != expected_keys or gate_accepts != 1439 or schema_repairs != 318:
        raise ValueError("public records do not reproduce the full case grid and gate totals")

    means = {}
    for row in read_csv(FROZEN / "method_summary.csv"):
        mode = row["method"]
        f1, oci = fmean(f1_by_method[mode]), fmean(oci_by_method[mode])
        check_number(f1, row["required_concept_f1_F1req_up"], f"{mode} mean F1")
        check_number(oci, row["oci_equal_weight_secondary"], f"{mode} mean OCI")
        means[mode] = {"n": len(f1_by_method[mode]), "method_conditioned_f1": f1, "oci_equal_weight": oci}
    print(json.dumps({
        "live_call_records": len(seen),
        "nonlive_fallback_records": 0,
        "schema_safe_finalizations": schema_repairs,
        "accepted_for_human_review": gate_accepts,
        "methods": means,
    }, indent=2))
    print("Frozen live evaluation replay: PASS")


if __name__ == "__main__":
    main()
