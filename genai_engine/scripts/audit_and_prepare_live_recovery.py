"""Audit paper-120 fallback rows and prepare live-LLM recovery reruns.

This script does not call Ollama. It reads the frozen paper-120 condition files,
exports the exact case IDs that need live reruns, and writes PowerShell commands
that rerun only those cases into a separate recovery output root.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paper120Condition:
    model: str
    method: str
    scenario_file: Path


FINAL_CONDITIONS = (
    Paper120Condition("qwen2_5_7b", "prompt_only", PROJECT_ROOT / "output/prompt_only_paper_120_qwen2_5_7b/20260701_220647/scenarios_prompt_only.jsonl"),
    Paper120Condition("qwen3_8b", "prompt_only", PROJECT_ROOT / "output/prompt_only_120_qwen3_8b/20260701_235448/scenarios_prompt_only.jsonl"),
    Paper120Condition("mistral_7b", "prompt_only", PROJECT_ROOT / "output/prompt_only_120_mistral_7b/20260703_013152/scenarios_prompt_only.jsonl"),
    Paper120Condition("qwen2_5_7b", "prompt_rag", PROJECT_ROOT / "output/psq_sco_120_qwen2_5_7b/20260630_205124/qwen2_5_7b/scenarios_prompt_rag.jsonl"),
    Paper120Condition("qwen3_8b", "prompt_rag", PROJECT_ROOT / "output/psq_sco_120_prompt_rag_qwen3_8b/20260702_025346/scenarios.jsonl"),
    Paper120Condition("mistral_7b", "prompt_rag", PROJECT_ROOT / "output/psq_sco_120_prompt_rag_mistral_7b_fixed/20260703_134043/scenarios.jsonl"),
    Paper120Condition("qwen2_5_7b", "ontology_prompt_rag", PROJECT_ROOT / "output/psq_sco_120_qwen2_5_7b/20260630_205124/qwen2_5_7b/scenarios_ontology_prompt_rag.jsonl"),
    Paper120Condition("qwen3_8b", "ontology_prompt_rag", PROJECT_ROOT / "output/psq_sco_120_ontology_prompt_rag_qwen3_8b/20260702_184521/scenarios.jsonl"),
    Paper120Condition("mistral_7b", "ontology_prompt_rag", PROJECT_ROOT / "output/psq_sco_120_ontology_prompt_rag_mistral_7b/20260704_000204/scenarios.jsonl"),
    Paper120Condition("qwen2_5_7b", "ontology_text_rag", PROJECT_ROOT / "output/psq_sco_120_ontology_text_rag_chroma_qwen2_5_7b_light/20260708_211811/scenarios_ontology_text_rag.jsonl"),
    Paper120Condition("qwen3_8b", "ontology_text_rag", PROJECT_ROOT / "output/psq_sco_120_ontology_text_rag_chroma_qwen3_8b_compact/20260709_141125/scenarios_ontology_text_rag.jsonl"),
    Paper120Condition("mistral_7b", "ontology_text_rag", PROJECT_ROOT / "output/psq_sco_120_ontology_text_rag_chroma_mistral_7b_compact/20260710_012836/scenarios_ontology_text_rag.jsonl"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare live-LLM recovery reruns for fallback paper-120 rows.")
    parser.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "output" / "paper120_live_llm_recovery_plan")
    parser.add_argument(
        "--include-validation-failed",
        action="store_true",
        help="Also rerun live rows whose scenario validation failed. Default only targets non-live/fallback/error rows.",
    )
    parser.add_argument("--llm-timeout", type=int, default=1200)
    parser.add_argument("--llm-max-tokens", type=int, default=1800)
    parser.add_argument("--llm-num-ctx", type=int, default=4096)
    parser.add_argument("--llm-temperature", type=float, default=0.2)
    parser.add_argument("--llm-parse-retries", type=int, default=2)
    parser.add_argument("--n-rag-examples", type=int, default=1)
    parser.add_argument("--ontology-text-doc-limit", type=int, default=4)
    parser.add_argument("--progress-heartbeat-seconds", type=int, default=30)
    parser.add_argument(
        "--recovery-output-root",
        type=Path,
        default=PROJECT_ROOT / "output" / "paper120_live_llm_recovery_runs",
        help="Root where generated recovery runs should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir / run_id
    case_dir = out_dir / "case_ids"
    out_dir.mkdir(parents=True, exist_ok=True)
    case_dir.mkdir(parents=True, exist_ok=True)

    detail_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    commands: List[str] = [
        "# Auto-generated live-LLM recovery commands for PSQ-SCO paper-120 fallback rows.",
        "# Run one block at a time. Each command stops if fallback is used again.",
        "cd genai_engine",
        '$PY = "python"',
        "Remove-Item Env:\\PSQ_KB_DIR -ErrorAction SilentlyContinue",
        "",
    ]

    total_rows = total_live = total_recovery = 0
    for condition in FINAL_CONDITIONS:
        rows = list(_read_jsonl(condition.scenario_file))
        fallback_case_ids: List[str] = []
        live_count = 0
        fallback_count = 0
        failed_count = 0
        validation_failed_count = 0
        for row in rows:
            case_id = _case_id(row)
            used_live = bool(row.get("used_live_llm"))
            used_fallback = bool(row.get("used_fallback"))
            has_error = bool(_generation_error(row))
            has_scenario = bool(row.get("scenario"))
            validation_passed = bool(row.get("validation_passed"))
            needs_recovery = (not used_live) or used_fallback or has_error or not has_scenario
            if args.include_validation_failed and not validation_passed:
                needs_recovery = True
            if used_live:
                live_count += 1
            if used_fallback:
                fallback_count += 1
            if has_error or not has_scenario:
                failed_count += 1
            if not validation_passed:
                validation_failed_count += 1
            if needs_recovery:
                fallback_case_ids.append(case_id)
                detail_rows.append(
                    {
                        "model": condition.model,
                        "method": condition.method,
                        "case_id": case_id,
                        "used_live_llm": used_live,
                        "used_fallback": used_fallback,
                        "validation_passed": validation_passed,
                        "has_generation_error": has_error,
                        "has_scenario": has_scenario,
                        "scenario_file": str(condition.scenario_file),
                    }
                )
        fallback_case_ids = sorted({case_id for case_id in fallback_case_ids if case_id})
        total_rows += len(rows)
        total_live += live_count
        total_recovery += len(fallback_case_ids)
        case_file = ""
        if fallback_case_ids:
            case_path = case_dir / f"{condition.model}__{condition.method}__case_ids.txt"
            case_path.write_text("\n".join(fallback_case_ids) + "\n", encoding="utf-8")
            case_file = str(case_path)
            commands.extend(_command_block(args, condition, case_path))
        summary_rows.append(
            {
                "model": condition.model,
                "method": condition.method,
                "total_rows": len(rows),
                "live_rows": live_count,
                "fallback_rows": fallback_count,
                "error_or_missing_scenario_rows": failed_count,
                "validation_failed_rows": validation_failed_count,
                "recovery_case_count": len(fallback_case_ids),
                "case_id_file": case_file,
                "scenario_file": str(condition.scenario_file),
            }
        )

    _write_csv(out_dir / "fallback_summary.csv", summary_rows)
    _write_csv(out_dir / "fallback_cases_long.csv", detail_rows)
    (out_dir / "rerun_fallback_live_commands.ps1").write_text("\n".join(commands) + "\n", encoding="utf-8")
    manifest = {
        "created_at": datetime.now().isoformat(),
        "total_rows": total_rows,
        "live_rows": total_live,
        "recovery_case_count": total_recovery,
        "fallback_or_non_live_rows": total_rows - total_live,
        "include_validation_failed": args.include_validation_failed,
        "output_files": {
            "fallback_summary_csv": str(out_dir / "fallback_summary.csv"),
            "fallback_cases_long_csv": str(out_dir / "fallback_cases_long.csv"),
            "rerun_commands_ps1": str(out_dir / "rerun_fallback_live_commands.ps1"),
            "case_id_dir": str(case_dir),
        },
    }
    (out_dir / "recovery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def _command_block(args: argparse.Namespace, condition: Paper120Condition, case_path: Path) -> List[str]:
    output_dir = args.recovery_output_root / f"{condition.model}__{condition.method}"
    lines = [
        f"# {condition.model} / {condition.method}",
        "& $PY .\\generate_scenarios_sco.py `",
        "  --case-set paper_120 `",
        f"  --mode {condition.method} `",
        f"  --llm {condition.model} `",
        f"  --case-id-file {case_path} `",
        f"  --n-rag-examples {args.n_rag_examples} `",
        f"  --ontology-text-doc-limit {args.ontology_text_doc_limit} `",
        f"  --llm-timeout {args.llm_timeout} `",
        f"  --llm-max-tokens {args.llm_max_tokens} `",
        f"  --llm-num-ctx {args.llm_num_ctx} `",
        f"  --llm-temperature {args.llm_temperature} `",
        f"  --llm-parse-retries {args.llm_parse_retries} `",
        f"  --progress-heartbeat-seconds {args.progress_heartbeat_seconds} `",
        "  --compact-generation-prompt `",
        "  --require-live-llm `",
        f"  --out-dir {output_dir}",
        "",
    ]
    return lines


def _read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def _case_id(row: Dict[str, Any]) -> str:
    case = row.get("case") if isinstance(row.get("case"), dict) else {}
    return str(case.get("case_id") or "")


def _generation_error(row: Dict[str, Any]) -> Any:
    prompt_metadata = row.get("prompt_metadata") if isinstance(row.get("prompt_metadata"), dict) else {}
    return prompt_metadata.get("generation_error") or prompt_metadata.get("live_llm_error")


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: List[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
