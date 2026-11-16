"""Build advisor-aligned evaluation, analysis, and presentation reporting artifacts.

The script reads the frozen 1,440-row live-recovered experiment and the PSQ-SCO
v9.1 validation bundle. It does not regenerate or rescore scenarios. Derived
tables are clearly labeled as post-hoc reporting analyses.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

import build_complete_psq_system_guide as doc_helpers


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "20260714_012218"
OUT_DIR = ROOT / "output" / "advisor_aligned_final_reporting" / RUN_ID
FIG_DIR = OUT_DIR / "figures"

GEN_DIR = ROOT / "output" / "paper120_live_recovered_final" / "20260712_183315"
SCENARIO_DIR = GEN_DIR / "generated_scenarios"
EVAL_DIR = (
    ROOT
    / "output"
    / "three_layer_eval_3models_120cases_4modes_live_recovered_standard_no_bertscore"
    / "20260712_184750"
)
ONTOLOGY_ROOT = Path(r"ontology")
ONTOLOGY_PATH = ONTOLOGY_ROOT / "ontology" / "personashield-psq-sco-v9.1.owl"
ONTOLOGY_OUT = ONTOLOGY_ROOT / "outputs" / "v9_1"
ADVISER_COMMENTS_PATH = Path(
    r"external-assets/pasted-text.txt"
)

METHOD_ORDER = ["prompt_only", "prompt_rag", "ontology_prompt_rag", "ontology_text_rag"]
METHOD_LABEL = {
    "prompt_only": "Prompt-only",
    "prompt_rag": "Prompt+RAG",
    "ontology_prompt_rag": "Ontology packet+Prompt+RAG",
    "ontology_text_rag": "Ontology-to-text+Prompt+RAG",
}
MODEL_LABEL = {
    "mistral_7b": "Mistral 7B",
    "qwen2_5_7b": "Qwen2.5 7B",
    "qwen3_8b": "Qwen3 8B",
}
COMPONENTS = [
    "json_validity",
    "control_adherence",
    "required_concept_f1",
    "grounding_completeness",
    "non_contradiction",
]
CURRENT_WEIGHTS = {
    "json_validity": 0.20,
    "control_adherence": 0.25,
    "required_concept_f1": 0.25,
    "grounding_completeness": 0.20,
    "non_contradiction": 0.10,
}
COLORS = {
    "prompt_only": "#65788A",
    "prompt_rag": "#2A7F86",
    "ontology_prompt_rag": "#3D7F5F",
    "ontology_text_rag": "#B88A2B",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a frozen source artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def f4(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "not available"
    return f"{float(value):.4f}"


def p1(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "not available"
    return f"{100 * float(value):.1f}%"


def sci(value: Any) -> str:
    if value is None:
        return "not available"
    return f"{float(value):.3e}"


def md_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    safe_rows = [[str(item).replace("|", "/").replace("\n", " ") for item in row] for row in rows]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in safe_rows)
    return "\n".join(lines)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    n = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.zeros(n, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = min(1.0, (n - rank) * float(p_values[idx]))
        running = max(running, candidate)
        adjusted[idx] = running
    return adjusted.tolist()


def load_final_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(SCENARIO_DIR.glob("*.jsonl")):
        method = next((item for item in METHOD_ORDER if f"__{item}__" in path.name), "unknown")
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw = json.loads(line)
                raw["_source_file"] = str(path)
                raw["_line_number"] = line_number
                raw["_method"] = method
                rows.append(raw)
    return rows


def derive_runtime_audit(rows: Sequence[dict[str, Any]], recovery: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail: list[dict[str, Any]] = []
    for raw in rows:
        scenario = raw.get("scenario") if isinstance(raw.get("scenario"), dict) else {}
        generation_meta = scenario.get("generation_meta") if isinstance(scenario.get("generation_meta"), dict) else {}
        top_prompt = raw.get("prompt_metadata") if isinstance(raw.get("prompt_metadata"), dict) else {}
        nested_prompt = generation_meta.get("prompt_metadata") if isinstance(generation_meta.get("prompt_metadata"), dict) else {}
        prompt_meta = {**nested_prompt, **top_prompt}
        rag_status = (
            prompt_meta.get("rag_runtime_status")
            or generation_meta.get("rag_runtime_status")
            or {}
        )
        model = raw.get("model") if isinstance(raw.get("model"), dict) else {}
        case = raw.get("case") if isinstance(raw.get("case"), dict) else {}
        detail.append(
            {
                "model_key": raw.get("llm_key"),
                "method": raw.get("_method"),
                "case_id": case.get("case_id"),
                "generation_meta_present": bool(generation_meta),
                "engine": generation_meta.get("engine"),
                "engine_version": generation_meta.get("engine_version"),
                "prompt_version": prompt_meta.get("prompt_version"),
                "system_chars": prompt_meta.get("system_chars"),
                "user_chars": prompt_meta.get("user_chars"),
                "external_rag_count": prompt_meta.get("external_rag_example_count"),
                "ontology_text_count": prompt_meta.get("ontology_text_rag_example_count"),
                "rag_status_present": bool(rag_status),
                "rag_available": rag_status.get("available") if isinstance(rag_status, dict) else None,
                "rag_indexed": rag_status.get("indexed") if isinstance(rag_status, dict) else None,
                "rag_total_documents": rag_status.get("total_documents") if isinstance(rag_status, dict) else None,
                "temperature": model.get("temperature"),
                "max_tokens": model.get("max_tokens"),
                "num_ctx": model.get("num_ctx"),
                "timeout": model.get("timeout"),
            }
        )
    detail_df = pd.DataFrame(detail)

    recovery_counts = (
        recovery.groupby(["model", "method"]).size().rename("recovered_replacements").reset_index().rename(columns={"model": "model_key"})
    )

    def values_text(series: pd.Series) -> str:
        values = sorted({str(value) for value in series.dropna().tolist() if str(value) not in {"", "None"}})
        return "; ".join(values) if values else "not recorded"

    summary_rows: list[dict[str, Any]] = []
    for (model_key, method), group in detail_df.groupby(["model_key", "method"], sort=True):
        ext = pd.to_numeric(group["external_rag_count"], errors="coerce")
        onto = pd.to_numeric(group["ontology_text_count"], errors="coerce")
        summary_rows.append(
            {
                "model_key": model_key,
                "method": method,
                "n": len(group),
                "generation_meta_rows": int(group["generation_meta_present"].sum()),
                "prompt_version_rows": int(group["prompt_version"].notna().sum()),
                "rag_status_rows": int(group["rag_status_present"].sum()),
                "rag_indexed_true_rows": int((group["rag_indexed"] == True).sum()),  # noqa: E712
                "rag_indexed_false_rows": int((group["rag_indexed"] == False).sum()),  # noqa: E712
                "external_rag_one_rows": int((ext == 1).sum()),
                "external_rag_zero_rows": int((ext == 0).sum()),
                "external_rag_metadata_missing_rows": int(ext.isna().sum()),
                "ontology_text_docs_mean": float(onto.mean()) if onto.notna().any() else None,
                "system_chars_mean_when_recorded": float(pd.to_numeric(group["system_chars"], errors="coerce").mean()),
                "user_chars_mean_when_recorded": float(pd.to_numeric(group["user_chars"], errors="coerce").mean()),
                "engines": values_text(group["engine"]),
                "engine_versions": values_text(group["engine_version"]),
                "prompt_versions": values_text(group["prompt_version"]),
                "temperatures": values_text(group["temperature"]),
                "max_tokens_values": values_text(group["max_tokens"]),
                "num_ctx_values": values_text(group["num_ctx"]),
            }
        )
    summary = pd.DataFrame(summary_rows).merge(recovery_counts, how="left", on=["model_key", "method"])
    summary["recovered_replacements"] = summary["recovered_replacements"].fillna(0).astype(int)
    return detail_df, summary


def derive_weight_analysis(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scores = scores.copy()
    scores["non_contradiction"] = 1.0 - scores["contradiction"]
    means = scores.groupby("method")[COMPONENTS].mean().loc[METHOD_ORDER]

    contributions = means.copy()
    for component in COMPONENTS:
        contributions[f"{component}_contribution"] = means[component] * CURRENT_WEIGHTS[component]
    contributions["derived_total"] = contributions[[f"{item}_contribution" for item in COMPONENTS]].sum(axis=1)
    contributions = contributions.reset_index()

    schemes = {
        "current_project_index": [0.20, 0.25, 0.25, 0.20, 0.10],
        "equal_five_components": [0.20, 0.20, 0.20, 0.20, 0.20],
        "concept_heavy_diagnostic": [0.10, 0.15, 0.40, 0.25, 0.10],
        "grounding_heavy_diagnostic": [0.10, 0.15, 0.20, 0.45, 0.10],
    }
    sensitivity_rows: list[dict[str, Any]] = []
    for scheme, weights in schemes.items():
        values = means.to_numpy() @ np.asarray(weights)
        ranks = pd.Series(values, index=METHOD_ORDER).rank(ascending=False, method="min").astype(int)
        for method, value in zip(METHOD_ORDER, values):
            sensitivity_rows.append(
                {
                    "scheme": scheme,
                    "method": method,
                    "score": float(value),
                    "rank": int(ranks[method]),
                    **{f"weight_{component}": weight for component, weight in zip(COMPONENTS, weights)},
                }
            )
    sensitivity = pd.DataFrame(sensitivity_rows)

    rng = np.random.default_rng(20260714)
    sampled_weights = rng.dirichlet(np.ones(len(COMPONENTS)), 100_000)
    sampled_scores = sampled_weights @ means.to_numpy().T
    winners = np.argmax(sampled_scores, axis=1)
    random_summary = pd.DataFrame(
        {
            "method": METHOD_ORDER,
            "win_count": [(winners == idx).sum() for idx in range(len(METHOD_ORDER))],
            "win_rate": [(winners == idx).mean() for idx in range(len(METHOD_ORDER))],
            "sampling_distribution": "Dirichlet(1,1,1,1,1)",
            "sample_count": 100_000,
            "seed": 20260714,
        }
    )

    leave_rows: list[dict[str, Any]] = []
    for dropped in COMPONENTS:
        kept = [component for component in COMPONENTS if component != dropped]
        values = means[kept].mean(axis=1)
        ranks = values.rank(ascending=False, method="min").astype(int)
        for method in METHOD_ORDER:
            leave_rows.append(
                {
                    "dropped_component": dropped,
                    "method": method,
                    "equal_weight_score_on_remaining_components": float(values[method]),
                    "rank": int(ranks[method]),
                }
            )
    leave_one_out = pd.DataFrame(leave_rows)
    return contributions, sensitivity, random_summary, leave_one_out


def derive_corrected_pairwise(scores: pd.DataFrame, source_statistics: dict[str, Any]) -> pd.DataFrame:
    pivot = scores.pivot_table(index=["model_key", "case_id"], columns="method", values="overall_conformance", aggfunc="first")
    source_comparisons = source_statistics["comparisons"]
    adjusted = holm_adjust([item["wilcoxon_signed_rank"]["p_value"] for item in source_comparisons])
    rows: list[dict[str, Any]] = []
    for source, holm_p in zip(source_comparisons, adjusted):
        left = source["left"]
        right = source["right"]
        diffs = (pivot[right] - pivot[left]).dropna().to_numpy()
        nonzero = diffs[diffs != 0]
        ranks = rankdata(np.abs(nonzero), method="average")
        positive_rank_sum = float(ranks[nonzero > 0].sum())
        negative_rank_sum = float(ranks[nonzero < 0].sum())
        true_rank_biserial = (positive_rank_sum - negative_rank_sum) / (positive_rank_sum + negative_rank_sum)
        sign_dominance = ((nonzero > 0).sum() - (nonzero < 0).sum()) / len(nonzero)
        rows.append(
            {
                "left": left,
                "right": right,
                "paired_n": source["paired_n"],
                "nonzero_n": len(nonzero),
                "mean_difference_right_minus_left": source["mean_difference_right_minus_left"],
                "ci95_low": source["bootstrap_ci95"][0],
                "ci95_high": source["bootstrap_ci95"][1],
                "wilcoxon_p_raw": source["wilcoxon_signed_rank"]["p_value"],
                "wilcoxon_p_holm": holm_p,
                "corrected_matched_rank_biserial": true_rank_biserial,
                "sign_dominance": sign_dominance,
                "legacy_mislabeled_field_value": source.get("rank_biserial_effect_size"),
            }
        )
    return pd.DataFrame(rows)


def derive_factor_breakdowns(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    details: list[pd.DataFrame] = []
    extrema: list[dict[str, Any]] = []
    for factor in ["role", "channel", "variant", "stage_id", "age_group_code"]:
        grouped = (
            scores.groupby(["method", factor])
            .agg(
                n=("overall_conformance", "size"),
                overall_conformance_mean=("overall_conformance", "mean"),
                required_concept_f1_mean=("required_concept_f1", "mean"),
                grounding_completeness_mean=("grounding_completeness", "mean"),
                contradiction_rate=("contradiction", "mean"),
            )
            .reset_index()
            .rename(columns={factor: "factor_value"})
        )
        grouped.insert(1, "factor", factor)
        details.append(grouped)
        for method in METHOD_ORDER:
            subset = grouped[grouped["method"] == method].sort_values("overall_conformance_mean")
            extrema.append(
                {
                    "factor": factor,
                    "method": method,
                    "lowest_group": subset.iloc[0]["factor_value"],
                    "lowest_mean": subset.iloc[0]["overall_conformance_mean"],
                    "highest_group": subset.iloc[-1]["factor_value"],
                    "highest_mean": subset.iloc[-1]["overall_conformance_mean"],
                    "range": subset["overall_conformance_mean"].max() - subset["overall_conformance_mean"].min(),
                }
            )
    return pd.concat(details, ignore_index=True), pd.DataFrame(extrema)


def derive_dataset_balance(dataset_sources: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    total_used = dataset_sources["used_document_count"].sum()
    for dimension, column in (("channel", "channel_folder"), ("language", "language"), ("variant", "variant_label"), ("source_origin", "source_origin")):
        grouped = dataset_sources.groupby(column)[["raw_document_count", "used_document_count"]].sum().reset_index()
        for _, item in grouped.iterrows():
            rows.append(
                {
                    "dimension": dimension,
                    "value": item[column],
                    "raw_document_count": int(item["raw_document_count"]),
                    "used_document_count": int(item["used_document_count"]),
                    "used_share": float(item["used_document_count"] / total_used),
                }
            )
    return pd.DataFrame(rows)


def derive_worked_example(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    selected: list[dict[str, Any]] = []
    for raw in rows:
        case = raw.get("case") if isinstance(raw.get("case"), dict) else {}
        if raw.get("llm_key") != "qwen3_8b" or case.get("case_id") != "PSQ-SCO-120-001":
            continue
        scenario = raw.get("scenario") if isinstance(raw.get("scenario"), dict) else {}
        selected.append(
            {
                "case_id": case.get("case_id"),
                "model_key": raw.get("llm_key"),
                "method": raw.get("_method"),
                "role": scenario.get("role"),
                "stage_id": scenario.get("stage_id"),
                "age_group_code": scenario.get("age_group_code"),
                "channel": scenario.get("channel"),
                "variant": scenario.get("variant"),
                "title": scenario.get("title"),
                "opening_hook": scenario.get("opening_hook"),
                "message": " / ".join(str(item) for item in (scenario.get("messages") or [])),
                "red_flags": "; ".join(str(item) for item in (scenario.get("red_flags") or [])),
                "correct_action": scenario.get("correct_action"),
                "hint_text": scenario.get("hint_text"),
                "used_live_llm": raw.get("used_live_llm"),
                "used_fallback": raw.get("used_fallback"),
            }
        )
    frame = pd.DataFrame(selected)
    frame["method_order"] = frame["method"].map({method: idx for idx, method in enumerate(METHOD_ORDER)})
    return frame.sort_values("method_order").drop(columns=["method_order"])


def create_figures(
    method_summary: pd.DataFrame,
    model_matrix: pd.DataFrame,
    diversity: pd.DataFrame,
    contributions: pd.DataFrame,
    sensitivity: pd.DataFrame,
    dataset_balance: pd.DataFrame,
    timing: pd.DataFrame,
    recovery: pd.DataFrame,
) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
        }
    )

    # Method metrics.
    metrics = ["overall_conformance", "required_concept_f1", "grounding_completeness", "ontology_semantic_scope"]
    metric_labels = ["Overall\nconformance", "Required-concept\nF1", "Grounding\ncompleteness", "Ontology\nsemantic scope"]
    fig, ax = plt.subplots(figsize=(11.5, 6.1))
    x = np.arange(len(metrics))
    width = 0.19
    for idx, method in enumerate(METHOD_ORDER):
        row = method_summary[method_summary["method"] == method].iloc[0]
        values = [row[item] for item in metrics]
        bars = ax.bar(x + (idx - 1.5) * width, values, width, label=METHOD_LABEL[method], color=COLORS[method])
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.012, f"{value:.3f}", ha="center", va="bottom", fontsize=7.4, rotation=90)
    ax.set_ylim(0, 1.12)
    ax.set_xticks(x, metric_labels)
    ax.set_ylabel("Mean automated score")
    ax.set_title("Latest method-level results: 360 scenarios per method")
    ax.grid(axis="y", color="#E2E7EC")
    ax.legend(ncol=2, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "method_results.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Weighted contribution chart.
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    bottom = np.zeros(len(METHOD_ORDER))
    component_colors = ["#4E79A7", "#76B7B2", "#59A14F", "#EDC948", "#E15759"]
    component_labels = ["JSON validity", "Control adherence", "Required-concept F1", "Grounding completeness", "Non-contradiction"]
    for component, color, label in zip(COMPONENTS, component_colors, component_labels):
        vals = []
        for method in METHOD_ORDER:
            row = contributions[contributions["method"] == method].iloc[0]
            vals.append(row[f"{component}_contribution"])
        ax.bar([METHOD_LABEL[item] for item in METHOD_ORDER], vals, bottom=bottom, label=label, color=color)
        bottom += np.asarray(vals)
    for idx, value in enumerate(bottom):
        ax.text(idx, value + 0.012, f"{value:.4f}", ha="center", weight="bold", color="#17365D")
    ax.set_ylim(0, 1.02)
    ax.set_ylabel("Contribution to project composite")
    ax.set_title("What creates the reported overall conformance score")
    ax.tick_params(axis="x", rotation=15)
    ax.legend(ncol=3, frameon=False, loc="upper center")
    ax.grid(axis="y", color="#E2E7EC")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "weighted_component_contributions.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Model heatmap.
    matrix = model_matrix.set_index("model_key")[METHOD_ORDER].loc[["mistral_7b", "qwen2_5_7b", "qwen3_8b"]].to_numpy()
    fig, ax = plt.subplots(figsize=(10.4, 4.8))
    image = ax.imshow(matrix, cmap="Blues", vmin=0.72, vmax=0.92, aspect="auto")
    ax.set_xticks(range(4), [METHOD_LABEL[item] for item in METHOD_ORDER], rotation=12, ha="right")
    ax.set_yticks(range(3), [MODEL_LABEL[item] for item in ["mistral_7b", "qwen2_5_7b", "qwen3_8b"]])
    ax.set_title("Model x method mean overall conformance")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.4f}", ha="center", va="center", weight="bold", color="white" if matrix[i, j] > 0.87 else "#17365D")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.04)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "model_method_heatmap.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Diversity.
    diversity = diversity.set_index("method").loc[METHOD_ORDER]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.5))
    x = np.arange(4)
    colors = [COLORS[item] for item in METHOD_ORDER]
    bars = axes[0].bar(x, diversity["embedding_diversity_mean"], color=colors)
    axes[0].set_xticks(x, [METHOD_LABEL[item] for item in METHOD_ORDER], rotation=22, ha="right")
    axes[0].set_ylim(0, 0.27)
    axes[0].set_title("Embedding Diversity: higher is more varied")
    axes[0].grid(axis="y", color="#E2E7EC")
    for bar, value in zip(bars, diversity["embedding_diversity_mean"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value + 0.005, f"{value:.3f}", ha="center")
    bars = axes[1].bar(x, diversity["self_bleu_mean"], color=colors)
    axes[1].set_xticks(x, [METHOD_LABEL[item] for item in METHOD_ORDER], rotation=22, ha="right")
    axes[1].set_ylim(0.72, 0.92)
    axes[1].set_title("Self-BLEU: lower is less repetitive")
    axes[1].grid(axis="y", color="#E2E7EC")
    for bar, value in zip(bars, diversity["self_bleu_mean"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 0.005, f"{value:.3f}", ha="center")
    fig.suptitle("Set-level diversity diagnostics use LaBSE and sacreBLEU", y=1.03, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "diversity_results.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Weight sensitivity.
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    schemes = list(sensitivity["scheme"].drop_duplicates())
    x = np.arange(len(schemes))
    width = 0.19
    for idx, method in enumerate(METHOD_ORDER):
        vals = [sensitivity[(sensitivity["scheme"] == scheme) & (sensitivity["method"] == method)]["score"].iloc[0] for scheme in schemes]
        ax.bar(x + (idx - 1.5) * width, vals, width, label=METHOD_LABEL[method], color=COLORS[method])
    ax.set_xticks(x, [item.replace("_", "\n") for item in schemes])
    ax.set_ylim(0.62, 0.94)
    ax.set_ylabel("Derived composite score")
    ax.set_title("Method ordering under four transparent diagnostic weight schemes")
    ax.legend(ncol=2, frameon=False)
    ax.grid(axis="y", color="#E2E7EC")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "weight_sensitivity.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Corpus balance.
    channel = dataset_balance[dataset_balance["dimension"] == "channel"].sort_values("used_document_count", ascending=False)
    language = dataset_balance[dataset_balance["dimension"] == "language"].sort_values("used_document_count", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.3))
    bars = axes[0].bar(channel["value"], channel["used_document_count"], color=["#4E79A7", "#76B7B2", "#F28E2B"])
    axes[0].set_title("Indexed-source candidates by channel folder")
    axes[0].set_ylabel("Documents after profile caps")
    for bar, count, share in zip(bars, channel["used_document_count"], channel["used_share"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2, count + 350, f"{int(count):,}\n({share:.1%})", ha="center", fontsize=9)
    bars = axes[1].bar(language["value"], language["used_document_count"], color=["#3D7F5F", "#B88A2B"])
    axes[1].set_title("Corpus language balance")
    for bar, count, share in zip(bars, language["used_document_count"], language["used_share"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2, count + 350, f"{int(count):,}\n({share:.1%})", ha="center", fontsize=9)
    fig.suptitle("The quality-profile RAG corpus is strongly email- and English-dominant", y=1.02, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "rag_corpus_balance.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Timing coverage.
    timing = timing.copy()
    timing["model_order"] = timing["model_key"].map({"mistral_7b": 0, "qwen2_5_7b": 1, "qwen3_8b": 2})
    timing["method_order"] = timing["method"].map({method: index for index, method in enumerate(METHOD_ORDER)})
    timing = timing.sort_values(["model_order", "method_order"]).reset_index(drop=True)
    timing["label"] = timing["model_key"].map(MODEL_LABEL) + "\n" + timing["method"].map(METHOD_LABEL)
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8.2), gridspec_kw={"height_ratios": [1, 1.2]})
    positions = np.arange(len(timing))
    axes[0].bar(positions, timing["direct_timing_n"], color="#2E74B5", label="Direct LLM-call timing rows")
    axes[0].bar(positions, timing["observed_timing_n"], bottom=timing["direct_timing_n"], color="#B8C4D1", label="Interarrival-only rows")
    axes[0].axhline(120, color="#A64B4B", linestyle="--", linewidth=1)
    axes[0].set_ylim(0, 130)
    axes[0].set_ylabel("Rows with timing evidence")
    axes[0].set_title("Timing telemetry coverage is heterogeneous")
    axes[0].set_xticks(positions)
    axes[0].tick_params(axis="x", labelbottom=False)
    axes[0].legend(frameon=False, ncol=2)
    direct = timing["direct_generation_seconds_mean"]
    axes[1].bar(positions, direct.fillna(0), color=[COLORS[item] for item in timing["method"]])
    axes[1].set_ylabel("Mean direct generation seconds")
    axes[1].set_xticks(positions, timing["label"], rotation=58, ha="right", fontsize=8)
    axes[1].set_title("Direct means only; zero-height bars have no direct telemetry")
    axes[1].grid(axis="y", color="#E2E7EC")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "timing_coverage.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Recovery replacements.
    recovery_counts = recovery.groupby(["model", "method"]).size().unstack(fill_value=0).reindex(index=["mistral_7b", "qwen2_5_7b", "qwen3_8b"], columns=METHOD_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(10.5, 5.3))
    bottom = np.zeros(len(recovery_counts))
    for method in METHOD_ORDER:
        vals = recovery_counts[method].to_numpy()
        ax.bar([MODEL_LABEL[item] for item in recovery_counts.index], vals, bottom=bottom, label=METHOD_LABEL[method], color=COLORS[method])
        bottom += vals
    for idx, total in enumerate(bottom):
        ax.text(idx, total + 6, f"{int(total)}", ha="center", weight="bold")
    ax.set_ylim(0, max(bottom) + 45)
    ax.set_ylabel("Rows replaced by live recovery")
    ax.set_title("649 earlier fallback/non-live rows replaced before final evaluation")
    ax.legend(ncol=2, frameon=False)
    ax.grid(axis="y", color="#E2E7EC")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "recovery_provenance.png", dpi=190, bbox_inches="tight")
    plt.close(fig)

    # Reuse the system diagrams generated for the complete guide.
    source_figures = ROOT / "docs" / "figures"
    for name in ["psq_complete_architecture.png", "psq_four_modes.png", "psq_ontology_validation_flow.png", "psq_paper120_design.png", "psq_three_layer_evaluation.png"]:
        shutil.copy2(source_figures / name, FIG_DIR / name)


def build_docx(markdown_path: Path, title: str, subtitle: str, filename: str) -> Path:
    source = markdown_path.read_text(encoding="utf-8")
    doc = Document()
    doc_helpers.configure_styles(doc)
    section = doc.sections[0]
    doc_helpers.configure_section(section)
    doc_helpers.configure_header_footer(section)
    doc.core_properties.title = title
    doc.core_properties.subject = subtitle
    doc.core_properties.author = "PersonaShield Quest research project"
    bullet_id, decimal_id = doc_helpers.add_numbering_definitions(doc)

    for _ in range(5):
        doc.add_paragraph()
    kicker = doc.add_paragraph()
    kicker.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = kicker.add_run("ADVISOR-ALIGNED RESEARCH REPORT  |  FROZEN DATASET")
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = doc_helpers.rgb(doc_helpers.GOLD)
    kicker.paragraph_format.space_after = Pt(18)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.size = Pt(27)
    run.font.bold = True
    run.font.color.rgb = doc_helpers.rgb(doc_helpers.NAVY)
    p.paragraph_format.space_after = Pt(12)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(subtitle)
    run.font.size = Pt(13)
    run.font.color.rgb = doc_helpers.rgb(doc_helpers.DARK_BLUE)
    p.paragraph_format.space_after = Pt(32)
    rule = doc.add_paragraph()
    rule.paragraph_format.left_indent = doc_helpers.Inches(1.2)
    rule.paragraph_format.right_indent = doc_helpers.Inches(1.2)
    doc_helpers.set_paragraph_border(rule, color=doc_helpers.BLUE, size="18")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(28)
    run = p.add_run("Evidence freeze: PSQ-SCO v9.1 | 120 cases x 3 models x 4 methods | 1,440 live outputs | Evaluation run 20260712_184750")
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = doc_helpers.rgb(doc_helpers.TEAL)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    run = p.add_run("Prepared 14 July 2026")
    run.font.size = Pt(10)
    run.font.color.rgb = doc_helpers.rgb(doc_helpers.GRAY)
    doc.add_page_break()

    headings = [line[3:] for line in source.splitlines() if line.startswith("## ")]
    doc_helpers.add_contents(doc, headings)
    doc_helpers.render_markdown(doc, source, bullet_id, decimal_id, figure_base=OUT_DIR)
    output = OUT_DIR / filename
    doc.save(output)
    return output


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib_cache"))

    method_summary = pd.read_csv(EVAL_DIR / "method_summary.csv")
    model_summary = pd.read_csv(EVAL_DIR / "model_method_summary.csv")
    model_matrix = pd.read_csv(EVAL_DIR / "model_method_matrix.csv")
    scores = pd.read_csv(EVAL_DIR / "scenario_scores.csv")
    errors = pd.read_csv(EVAL_DIR / "error_analysis_paper_labels.csv")
    timing = pd.read_csv(EVAL_DIR / "timing_analysis.csv")
    diversity = pd.read_csv(EVAL_DIR / "semantic_diversity_method_summary.csv")
    diversity_by_model = pd.read_csv(EVAL_DIR / "semantic_diversity.csv")
    dataset_sources = pd.read_csv(EVAL_DIR / "dataset_sources.csv")
    manual_sample = pd.read_csv(EVAL_DIR / "manual_inspection_sample.csv")
    recovery = pd.read_csv(GEN_DIR / "recovered_replacements.csv")
    source_statistics = read_json(EVAL_DIR / "paired_statistics.json")
    dataset_description = read_json(EVAL_DIR / "dataset_description.json")
    run_metadata = read_json(EVAL_DIR / "run_metadata.json")
    merge_summary = read_json(GEN_DIR / "merge_summary.json")
    ontology_validation = read_json(EVAL_DIR / "ontology_validation.json")
    release_validation = read_json(ONTOLOGY_OUT / "release-validation-report.json")
    kg_completeness = read_json(ONTOLOGY_OUT / "kg-completeness-report.json")
    final_rows = load_final_rows()

    frozen_source_files = [
        ADVISER_COMMENTS_PATH,
        ONTOLOGY_PATH,
        ONTOLOGY_OUT / "release-validation-report.json",
        ONTOLOGY_OUT / "kg-completeness-report.json",
        GEN_DIR / "merge_summary.json",
        GEN_DIR / "recovered_replacements.csv",
        EVAL_DIR / "method_summary.csv",
        EVAL_DIR / "model_method_summary.csv",
        EVAL_DIR / "model_method_matrix.csv",
        EVAL_DIR / "scenario_scores.csv",
        EVAL_DIR / "error_analysis_paper_labels.csv",
        EVAL_DIR / "paired_statistics.json",
        EVAL_DIR / "dataset_description.json",
        EVAL_DIR / "dataset_sources.csv",
        EVAL_DIR / "timing_analysis.csv",
        EVAL_DIR / "semantic_diversity_method_summary.csv",
        EVAL_DIR / "semantic_diversity.csv",
        EVAL_DIR / "manual_inspection_sample.csv",
        EVAL_DIR / "run_metadata.json",
        EVAL_DIR / "ontology_validation.json",
        *sorted(SCENARIO_DIR.glob("*.jsonl")),
    ]
    source_hash_manifest = {
        "algorithm": "SHA-256",
        "purpose": "Integrity evidence for the frozen ontology, generation rows, and evaluation inputs used by this reporting bundle.",
        "files": [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in frozen_source_files
        ],
    }
    (OUT_DIR / "source_artifact_hashes.json").write_text(
        json.dumps(source_hash_manifest, indent=2), encoding="utf-8"
    )

    runtime_detail, runtime_summary = derive_runtime_audit(final_rows, recovery)
    contributions, sensitivity, random_weight_summary, leave_one_out = derive_weight_analysis(scores)
    corrected_pairs = derive_corrected_pairwise(scores, source_statistics)
    factor_details, factor_extrema = derive_factor_breakdowns(scores)
    dataset_balance = derive_dataset_balance(dataset_sources)
    worked_example = derive_worked_example(final_rows)
    recovery_summary = recovery.groupby(["model", "method"]).size().rename("replacement_count").reset_index()

    def method_metric(method: str, column: str) -> float:
        return float(method_summary.loc[method_summary["method"] == method, column].iloc[0])

    best_cell = model_summary.loc[model_summary["overall_conformance_mean"].idxmax()]
    email_share = float(dataset_balance.loc[(dataset_balance["dimension"] == "channel") & (dataset_balance["value"] == "email"), "used_share"].iloc[0])
    english_share = float(dataset_balance.loc[(dataset_balance["dimension"] == "language") & (dataset_balance["value"] == "en"), "used_share"].iloc[0])
    direct_diversity = diversity.loc[diversity["method"] == "ontology_prompt_rag"].iloc[0]
    baseline_diversity = diversity.loc[diversity["method"] == "prompt_only"].iloc[0]
    presentation_core_data = pd.DataFrame(
        [
            ["Design", "Full scenario design space", "1,350", "5 roles x 9 stages x 5 ages x 3 channels x 2 variants", "The experiment samples this space; it does not generate all 1,350 slots.", "Paper-120 case manifest"],
            ["Design", "Matched case specifications", "120", "The same case IDs are supplied to every model and method.", "Cases are inputs, not fixed output stories or human judgments.", "Paper-120 case manifest"],
            ["Design", "Final outputs", f"{merge_summary['total_rows']:,}", "120 cases x 3 local models x 4 methods", "Rows are scenario artifacts, not learner observations.", "merge_summary.json"],
            ["Integrity", "Live LLM rows", f"{merge_summary['live_rows']:,}", "All final rows are marked live after recovery.", "Live status does not mean untouched model text because repair/rebinding follows generation.", "merge_summary.json"],
            ["Integrity", "Remaining fallback rows", f"{merge_summary['remaining_non_live_rows']:,}", "No fallback row remains in the frozen final bundle.", "The bundle still combines original and recovery executions.", "merge_summary.json"],
            ["Integrity", "Recovery replacements", f"{merge_summary['recovery_replacements']:,}", "Earlier fallback/non-live rows replaced before final evaluation.", "Recovery provenance is a pipeline-level confound.", "recovered_replacements.csv"],
            ["Ontology", "Release structure", f"{release_validation['counts']['classes']} classes; {release_validation['counts']['individuals']} individuals; {release_validation['triple_count']:,} triples", "Authoritative PSQ-SCO v9.1 release counts.", "The lightweight parser reports 74 classes under a different counting convention.", "release-validation-report.json"],
            ["Ontology", "HermiT result", "PASS; 0 unsatisfiable", f"Recorded logical consistency run completed in {release_validation['reasoner']['duration_seconds']:.3f} seconds.", "Formal consistency does not prove domain truth or universal completeness.", "release-validation-report.json"],
            ["Ontology", "SPARQL ASK", f"{release_validation['ask_validation']['passed']}/{release_validation['ask_validation']['total']}", "All encoded competency-query ASK checks passed.", "Only the implemented query cases are tested.", "release-validation-report.json"],
            ["Ontology", "CQ-bounded completeness", f"{kg_completeness['passed_checks']:,}/{kg_completeness['required_checks']:,}", "All required checks passed for CQ1-CQ4.", "This is explicitly bounded, not universal knowledge completeness.", "kg-completeness-report.json"],
            ["Method result", "Prompt-only overall conformance", f"{method_metric('prompt_only', 'overall_conformance'):.4f}", "Lowest method mean.", "Author-defined operational index, not percentage quality.", "method_summary.csv"],
            ["Method result", "Prompt+RAG overall conformance", f"{method_metric('prompt_rag', 'overall_conformance'):.4f}", "External retrieval improves the project index over Prompt-only.", "Retrieval availability and prompt/runtime metadata are heterogeneous.", "method_summary.csv"],
            ["Method result", "Direct ontology packet overall conformance", f"{method_metric('ontology_prompt_rag', 'overall_conformance'):.4f}", "Highest method mean and best within every tested model.", "Supports pipeline conformance, not deployability or learning effectiveness.", "method_summary.csv"],
            ["Method result", "Ontology-to-text overall conformance", f"{method_metric('ontology_text_rag', 'overall_conformance'):.4f}", "Second-highest method mean.", "This is ontology-to-text context, not Microsoft GraphRAG.", "method_summary.csv"],
            ["Method result", "Best model-method cell", f"{MODEL_LABEL[best_cell['model_key']]} + {METHOD_LABEL[best_cell['method']]} = {best_cell['overall_conformance_mean']:.4f}", "Qwen3 benefits most from the direct packet.", "No model is universally best across every method.", "model_method_summary.csv"],
            ["Effect", "Direct packet minus Prompt-only", f"{method_metric('ontology_prompt_rag', 'overall_conformance') - method_metric('prompt_only', 'overall_conformance'):+.4f}", "Largest headline matched-method difference.", "The effect applies to the implemented operational index.", "paired_statistics.json + corrected post-hoc table"],
            ["Effect", "Direct packet minus Prompt+RAG", f"{method_metric('ontology_prompt_rag', 'overall_conformance') - method_metric('prompt_rag', 'overall_conformance'):+.4f}", "Direct ontology structure outperforms external vector RAG in this pipeline.", "Prompt length, repair, and recovery provenance are not perfectly homogeneous.", "paired_statistics.json + corrected post-hoc table"],
            ["Diversity", "Prompt-only Embedding Diversity / Self-BLEU", f"{baseline_diversity['embedding_diversity_mean']:.4f} / {baseline_diversity['self_bleu_mean']:.4f}", "Baseline is the most repetitive by both diagnostics.", "No universal acceptance threshold applies.", "semantic_diversity_method_summary.csv"],
            ["Diversity", "Direct packet Embedding Diversity / Self-BLEU", f"{direct_diversity['embedding_diversity_mean']:.4f} / {direct_diversity['self_bleu_mean']:.4f}", "Best relative diversity result among tested methods.", "Absolute repetition remains high; inspect near-duplicate pairs manually.", "semantic_diversity_method_summary.csv"],
            ["RAG corpus", "Email share after caps", f"{email_share:.1%}", "External corpus is strongly email-dominant.", "Channel comparisons are not equally supported by source volume.", "dataset_sources.csv"],
            ["RAG corpus", "English share after caps", f"{english_share:.1%}", "External corpus is strongly English-dominant.", "Multilingual claims require broader and more balanced evidence.", "dataset_sources.csv"],
            ["Human validation", "Completed manual acceptability ratings", f"{int(manual_sample['manual_acceptability'].notna().sum())}/{len(manual_sample)}", "A 24-row stratified worksheet exists, but ratings are blank.", "Usability, pedagogy, factual faithfulness, and deployability are not yet established.", "manual_inspection_sample.csv"],
            ["Weight robustness", "Random weight vectors won by direct packet", f"{float(random_weight_summary.loc[random_weight_summary['method'] == 'ontology_prompt_rag', 'win_rate'].iloc[0]):.3%}", "Ranking is robust across 100,000 sampled non-negative unit-sum vectors.", "This tests ranking sensitivity, not normative coefficient validity.", "derived_random_weight_robustness.csv"],
        ],
        columns=["section", "metric", "value", "presentation_interpretation", "claim_boundary", "source_artifact"],
    )

    derived_files = {
        "derived_component_contributions.csv": contributions,
        "derived_weight_sensitivity.csv": sensitivity,
        "derived_random_weight_robustness.csv": random_weight_summary,
        "derived_leave_one_component_out.csv": leave_one_out,
        "derived_corrected_pairwise_statistics.csv": corrected_pairs,
        "derived_factor_breakdowns.csv": factor_details,
        "derived_factor_extrema.csv": factor_extrema,
        "derived_dataset_balance.csv": dataset_balance,
        "derived_runtime_metadata_detail.csv": runtime_detail,
        "derived_runtime_metadata_summary.csv": runtime_summary,
        "derived_recovery_distribution.csv": recovery_summary,
        "worked_example_qwen3_case001.csv": worked_example,
        "presentation_core_data.csv": presentation_core_data,
    }
    for name, frame in derived_files.items():
        frame.to_csv(OUT_DIR / name, index=False, encoding="utf-8-sig")

    create_figures(method_summary, model_matrix, diversity, contributions, sensitivity, dataset_balance, timing, recovery)

    method_table = md_table(
        ["Method", "n", "Schema", "Control", "Concept P", "Concept R", "Concept F1", "Grounding", "Ontology scope", "Contradiction", "Overall", "95% CI"],
        [
            [
                METHOD_LABEL[row.method],
                int(row.n),
                f4(row.schema_completeness),
                f4(row.control_adherence),
                f4(row.required_concept_precision),
                f4(row.required_concept_recall),
                f4(row.required_concept_f1),
                f4(row.grounding_completeness),
                f4(row.ontology_semantic_scope),
                f4(row.contradiction_rate),
                f4(row.overall_conformance),
                f"[{f4(row.overall_conformance_ci95_low)}, {f4(row.overall_conformance_ci95_high)}]",
            ]
            for row in method_summary.itertuples(index=False)
        ],
    )

    contribution_table = md_table(
        ["Method", "JSON contribution", "Control contribution", "Concept-F1 contribution", "Grounding contribution", "Non-contradiction contribution", "Total"],
        [
            [
                METHOD_LABEL[row.method],
                f4(row.json_validity_contribution),
                f4(row.control_adherence_contribution),
                f4(row.required_concept_f1_contribution),
                f4(row.grounding_completeness_contribution),
                f4(row.non_contradiction_contribution),
                f4(row.derived_total),
            ]
            for row in contributions.itertuples(index=False)
        ],
    )

    model_table = md_table(
        ["Model", "Prompt-only", "Prompt+RAG", "Ontology packet", "Ontology-to-text"],
        [
            [
                MODEL_LABEL[row.model_key],
                f4(row.prompt_only),
                f4(row.prompt_rag),
                f4(row.ontology_prompt_rag),
                f4(row.ontology_text_rag),
            ]
            for row in model_matrix.itertuples(index=False)
        ],
    )

    error_table = md_table(
        ["Error or diagnostic", "Prompt-only", "Prompt+RAG", "Ontology packet", "Ontology-to-text", "Interpretation"],
        [
            [
                row.error_type,
                int(row.prompt_only),
                int(row.prompt_rag),
                int(row.ontology_prompt_rag),
                int(row.ontology_text_rag),
                row.interpretation,
            ]
            for row in errors.itertuples(index=False)
        ],
    )

    diversity_table = md_table(
        ["Method", "Embedding Diversity", "Mean cosine", "Self-BLEU", "1 - Self-BLEU", "Interpretation"],
        [
            [
                METHOD_LABEL[row.method],
                f4(row.embedding_diversity_mean),
                f4(row.mean_pairwise_cosine_similarity_mean),
                f4(row.self_bleu_mean),
                f4(row.self_bleu_diversity_mean),
                "Relative diagnostic only; no universal pass threshold",
            ]
            for row in diversity.itertuples(index=False)
        ],
    )

    corrected_pair_table = md_table(
        ["Comparison (right - left)", "Mean difference", "95% bootstrap CI", "Raw p", "Holm p", "Corrected rank-biserial", "Sign dominance"],
        [
            [
                f"{METHOD_LABEL[row.right]} - {METHOD_LABEL[row.left]}",
                f4(row.mean_difference_right_minus_left),
                f"[{f4(row.ci95_low)}, {f4(row.ci95_high)}]",
                sci(row.wilcoxon_p_raw),
                sci(row.wilcoxon_p_holm),
                f4(row.corrected_matched_rank_biserial),
                f4(row.sign_dominance),
            ]
            for row in corrected_pairs.itertuples(index=False)
        ],
    )

    factor_table = md_table(
        ["Factor", "Method", "Lowest group", "Lowest mean", "Highest group", "Highest mean", "Range"],
        [
            [
                row.factor,
                METHOD_LABEL[row.method],
                row.lowest_group,
                f4(row.lowest_mean),
                row.highest_group,
                f4(row.highest_mean),
                f4(row.range),
            ]
            for row in factor_extrema.itertuples(index=False)
        ],
    )

    rag_balance_table = md_table(
        ["Dimension", "Value", "Raw records", "After caps", "Share of after-cap corpus"],
        [
            [row.dimension, row.value, f"{int(row.raw_document_count):,}", f"{int(row.used_document_count):,}", p1(row.used_share)]
            for row in dataset_balance[dataset_balance["dimension"].isin(["channel", "language", "variant"])].itertuples(index=False)
        ],
    )

    runtime_table = md_table(
        ["Model", "Method", "Rows", "Recovered", "Generation meta", "RAG-status meta", "RAG indexed true", "External example=1", "External example=0", "External-count missing"],
        [
            [
                MODEL_LABEL[row.model_key],
                METHOD_LABEL[row.method],
                int(row.n),
                int(row.recovered_replacements),
                int(row.generation_meta_rows),
                int(row.rag_status_rows),
                int(row.rag_indexed_true_rows),
                int(row.external_rag_one_rows),
                int(row.external_rag_zero_rows),
                int(row.external_rag_metadata_missing_rows),
            ]
            for row in runtime_summary.sort_values(["model_key", "method"]).itertuples(index=False)
        ],
    )

    timing_table = md_table(
        ["Model", "Method", "Direct n", "Direct mean s", "Direct median s", "Interarrival n", "Interarrival mean s", "Live rate", "Fallback rate"],
        [
            [
                MODEL_LABEL[row.model_key],
                METHOD_LABEL[row.method],
                int(row.direct_timing_n),
                f4(row.direct_generation_seconds_mean),
                f4(row.direct_generation_seconds_median),
                int(row.observed_timing_n),
                f4(row.observed_interarrival_seconds_mean),
                p1(row.live_llm_rate),
                p1(row.fallback_rate),
            ]
            for row in timing.itertuples(index=False)
        ],
    )

    worked_table = md_table(
        ["Method", "Title", "Opening hook", "Red flags", "Correct action"],
        [
            [METHOD_LABEL[row.method], row.title, row.opening_hook, row.red_flags, row.correct_action]
            for row in worked_example.itertuples(index=False)
        ],
    )

    current_alt = sensitivity[sensitivity["scheme"].isin(["current_project_index", "equal_five_components", "concept_heavy_diagnostic", "grounding_heavy_diagnostic"])]
    sensitivity_table = md_table(
        ["Weight scheme", "Prompt-only", "Prompt+RAG", "Ontology packet", "Ontology-to-text", "Top method"],
        [
            [
                scheme,
                f4(current_alt[(current_alt.scheme == scheme) & (current_alt.method == "prompt_only")].score.iloc[0]),
                f4(current_alt[(current_alt.scheme == scheme) & (current_alt.method == "prompt_rag")].score.iloc[0]),
                f4(current_alt[(current_alt.scheme == scheme) & (current_alt.method == "ontology_prompt_rag")].score.iloc[0]),
                f4(current_alt[(current_alt.scheme == scheme) & (current_alt.method == "ontology_text_rag")].score.iloc[0]),
                METHOD_LABEL[current_alt[current_alt.scheme == scheme].sort_values("score", ascending=False).iloc[0].method],
            ]
            for scheme in current_alt.scheme.drop_duplicates()
        ],
    )

    evaluation_report = f"""# Final Detailed Evaluation and Results Report

Version 1.0 | Advisor-aligned frozen evidence report | 14 July 2026

## Executive Summary

This report evaluates the latest completed PersonaShield Quest scenario-generation experiment using the authoritative PSQ-SCO v9.1 ontology and the live-recovered 120-case output set. The experimental unit is a frozen case specification, not an arbitrary generated story. Every model receives the same 120 case IDs in every method. The design contains three local open-weight LLMs and four generation methods, producing `120 x 3 x 4 = 1,440` final rows.

All 1,440 final rows are marked as live LLM outputs and zero are marked as fallback outputs. This status was achieved after 649 earlier fallback or non-live rows were replaced from recovery runs. The final bundle therefore represents a completed pipeline dataset, but it combines original and recovery executions and does not retain complete prompt/runtime metadata for every row.

The highest current project-defined overall-conformance mean is 0.8860 for Ontology packet+Prompt+RAG. Ontology-to-text+Prompt+RAG is second at 0.8491, Prompt+RAG is third at 0.8181, and Prompt-only is fourth at 0.7741. The ordering is robust under the transparent alternative weight schemes and random non-negative weight vectors tested in this report. However, the numerical scale is not calibrated to human quality or learning gain. The component metrics, not the single composite, are the primary evidence.

The ontology passed the recorded formal and bounded checks: HermiT consistency PASS, zero unsatisfiable classes, eight of eight SPARQL ASK tests passed, and 4,362 of 4,362 CQ-bounded completeness checks passed. Runtime mapping also passed for all 1,440 rows. These results establish formal consistency and coverage of CQ1-CQ4 only; they do not establish universal cybersecurity completeness or educational effectiveness.

The strongest practical concern is content repetition. Mean Embedding Diversity ranges from 0.1865 to 0.2339 and mean Self-BLEU ranges from 0.7906 to 0.8846. The ontology-guided methods improve relative diversity over Prompt-only, but all four conditions remain semantically and lexically repetitive. The manual-inspection worksheet contains 24 stratified rows, but its human-rating fields are blank. Usability, pedagogy, factual faithfulness, and deployment acceptability therefore remain unvalidated by experts.

### Publication-Safe Verdict

The data support a bounded pipeline claim: direct ontology packets improve automated case, concept, grounding, and ontology-trace conformance relative to the tested baselines under matched conditions. The data do not support a claim that the generated scenarios are already proven usable, pedagogically effective, factually faithful, or diverse enough for deployment.

[[FIGURE:figures/psq_complete_architecture.png|Figure 1. Relationship among the ontology, local generation engine, structured outputs, experiment evaluator, and PCUE quality validator.]]

## 1. Research Problem and Evaluation Question

PersonaShield Quest requires complete game scenarios for five workplace roles, nine macro/micro stages, five age groups, three communication channels, and fake/real variants. This yields 1,350 scenario slots. Generating text is easy; generating consistent, safe, traceable, role-appropriate, stage-appropriate, and non-repetitive game content is the research problem.

The evaluation asks: when the same case specification and local model are held constant, how do Prompt-only, vector RAG, a direct structured ontology packet, and ontology-derived text context differ in automated conformance, traceability, repetition, and generation behavior?

The object of this experiment is the generated scenario artifact. Learner performance, knowledge gain, delayed retention, and workplace transfer are outside the current dataset.

## 2. Frozen Evidence Bundle

| Item | Frozen artifact |
| --- | --- |
| Adviser comments | `{ADVISER_COMMENTS_PATH}` |
| Ontology | `{ONTOLOGY_PATH}` |
| Ontology release | PSQ-SCO v9.1.0 |
| Final generated rows | `{GEN_DIR}` |
| Generation merge time | {merge_summary['created_at']} |
| Final evaluation | `{EVAL_DIR}` |
| Evaluation run ID | {run_metadata['run_id']} |
| BERTScore | Disabled in the paper-facing run |
| Embedding diversity backend | {run_metadata['diversity_embedding_backend']} |
| Embedding model | `{run_metadata['diversity_embedding_model']}` |
| Final row count | {merge_summary['total_rows']:,} |
| Live rows | {merge_summary['live_rows']:,} |
| Remaining fallback/non-live rows | {merge_summary['remaining_non_live_rows']:,} |
| Recovery replacements | {merge_summary['recovery_replacements']:,} |

No result from an earlier fallback-containing bundle is used as the main paper result in this report.

## 3. What the 120 Cases Mean

The 120 cases are 120 input specifications. They are not 120 fixed output stories and they are not 120 human-labeled scenario-quality judgments.

1. Three channels x two variants x five roles create 30 base groups.
2. Each base group is tested at Beginner Introductory, Intermediate Developing, and Expert Advanced, creating 90 anchor cases.
3. One balanced repetition is added to each group. These 30 cases rotate across the six non-anchor stages and all five age groups.
4. The total is `90 + 30 = 120`.

The design has 24 cases per role, 40 per channel, 60 per variant, 30 per difficulty condition, and 24 per age group. The same case IDs `PSQ-SCO-120-001` through `PSQ-SCO-120-120` occur for every model and method. The matched-case audit reports 120 of 120 complete four-method blocks for each model.

[[FIGURE:figures/psq_paper120_design.png|Figure 2. Construction of the 120 matched cases and the final 1,440-row factorial dataset.]]

## 4. Exact Four-Method Definitions

### 4.1 Prompt-only

The baseline receives the frozen case controls, persona/game schema, and prompt template. It receives no external retrieved examples and no ontology-derived packet or ontology-derived text. In the final merged bundle, Qwen2.5 and most Qwen3 Prompt-only rows came from the separate `prompt_only_generation` v1.0 engine, while Mistral Prompt-only rows contain mixed metadata from the PSQ-SCO engine and older rows. This is a pipeline-level baseline, not a perfectly prompt-length-matched ablation.

### 4.2 Prompt+RAG

The engine queries the external quality-profile corpus through ChromaDB when the vector index is available. Retrieval starts with `max(n_results x 16, 64)` candidates, then applies channel, language, retrieval mode, scam/ham, knowledge type, difficulty, age, and stage filters through fallback ladders. The final requested number is one external example, but retrieval sometimes returns zero and some older rows lack the count metadata.

### 4.3 Ontology packet+Prompt+RAG

The method uses the same external RAG path and additionally injects a structured semantic packet. The current code parses the OWL/RDF XML locally and selects templates, required rules, and evidence records by deterministic local subgraph filtering. It supplies must-include, must-exclude, quality-control, validation, and provenance fields.

Important correction: SPARQL validates the ontology in Layer 1, but the scenario generator does not execute the competency-query SPARQL files to build each runtime packet. Describing this method as “SPARQL-driven generation” would be inaccurate for the inspected code.

### 4.4 Ontology-to-text+Prompt+RAG

The method uses external RAG and also converts 324 ontology records into text documents. The static corpus contains 74 class records, 49 object-property records, 39 datatype-property records, 12 evidence-source records, six template records, 10 records detected by the broad generator rule predicate, and 134 other ontology records. For each case, deterministic scoring selects relevant record verbalizations and adds a Graph-CoT-inspired reasoning-interaction-execution document plus a selected-subgraph walk. The final run records four ontology-text documents per row where this metadata is retained.

Important correction: these ontology documents are not inserted into the Chroma external vector index. They are scored in memory by the ontology-text module and injected through the prompt's RAG-context shape. This is ontology-to-text RAG context, not the Microsoft GraphRAG architecture.

[[FIGURE:figures/psq_four_modes.png|Figure 3. The information supplied to each generation method.]]

## 5. Why the Method Is Not Microsoft-Style GraphRAG

Microsoft GraphRAG builds a graph from an input corpus and supports graph-organized local or global search, including entity neighborhoods and community reports. The inspected PersonaShield Quest code starts from an existing OWL ontology, verbalizes selected records, constructs deterministic graph traces, and injects the resulting text. It does not build community summaries, retrieve from a graph database at query time, or perform Microsoft GraphRAG local/global search.

The accurate labels are “structured ontology packet prompting” for Method 3 and “ontology-to-text RAG context” for Method 4. The graph traversal and Graph-CoT-inspired trace are genuine graph-derived components, but they do not make the complete pipeline equivalent to Microsoft GraphRAG.

## 6. Ontology Validation

The authoritative ontology is OWL 2/RDF XML at `{ONTOLOGY_PATH}`. The release validator counts 73 domain classes, 49 object properties, 39 data properties, 17 annotation properties, 133 named individuals, and 3,229 triples. The lightweight generation/evaluation parser reports 74 classes because it uses a different XML record-counting convention. Publication tables should use the release count of 73 and state the counting procedure.

| Validation view | Result | Meaning | Boundary |
| --- | --- | --- | --- |
| HermiT | PASS; consistent; 0 unsatisfiable classes; 3.636 seconds | No formal logical contradiction was found by the recorded reasoner run | Does not prove domain truth or completeness |
| SPARQL ASK | 8 of 8 passed with RDFLib 7.6.0 | Required competency-query patterns are present | Tests only the encoded query cases |
| CQ-bounded completeness | 4,362 of 4,362 | Required CQ1-CQ4 checks are present | Explicitly not universal completeness |
| Runtime mapping | 1,440 of 1,440 | Final rows preserve frozen case mappings after pipeline processing | Partly reflects deterministic rebinding |
| Noise analysis | 0 dangling local references; 0 removed-scope hits | No detected forbidden-scope leakage in the release checks | Limited to the implemented checks and term list |

The release has six scenario templates: two per channel, three fake and three real, and two at each of the three difficulty levels. The bounded completeness report identifies eight required quality-control rules. The generation adapter's broader predicate detects 10 records because it includes any identifier/type matching Rule or Constraint. These counts describe different selection conventions and should not be mixed without explanation.

One artifact-cleanliness issue remains: the v9.1 HermiT JSON points its stdout/stderr fields to an `outputs\\v8.2\\reasoner_runtime` path even though the ontology field identifies v9.1. The consistency result is recorded for the v9.1 path, but those auxiliary paths should be corrected before archival publication.

[[FIGURE:figures/psq_ontology_validation_flow.png|Figure 4. Formal reasoning, competency-query, bounded-completeness, and runtime-mapping validation.]]

## 7. External RAG Dataset

The quality profile selects 23 JSONL files. There are 87,661 raw rows before caps, 29,731 rows after profile caps, 28,728 indexed documents, and 1,003 exact-lowercase-hash duplicates skipped. One JSONL record becomes one retrieval document by concatenating available text, subject, body, message, dialogue, and cue fields. There is no overlapping fixed-size chunking step in this configuration.

The vector store is ChromaDB PersistentClient using cosine HNSW. The code does not pass a custom embedding function, so the exact embedding model depends on the installed Chroma default and is not frozen explicitly in the result metadata. This is a reproducibility gap. No explicit similarity threshold or reranker is implemented; Chroma ranking is filtered by metadata and fallback ladders.

{rag_balance_table}

The after-cap corpus is 89.9% email-folder material, 7.2% SMS, and 2.8% voice. It is 97.3% English and 2.7% Thai. This imbalance matters: channel and multilingual results cannot be interpreted as equally evidenced by the retrieval corpus. Voice generation relies on only 840 after-cap records, of which just 30 are the IRS phone-scam transcript source; several voice-folder records originate from SMS or generic project exports.

[[FIGURE:figures/rag_corpus_balance.png|Figure 5. Channel and language imbalance in the external quality-profile RAG corpus.]]

## 8. Generation and Post-Processing

The three local open-weight models are Qwen2.5 7B Instruct, Qwen3 8B, and Mistral 7B through Ollama. Configured defaults are temperature 0.45 for Qwen2.5/Qwen3 and 0.50 for Mistral, with model-dependent context and output limits. Recovery runs used overrides, compact prompts, and different historical engine versions in some cells. Therefore the experiment compares completed pipelines, not an isolated ontology variable under perfectly identical token budgets.

Every live response enters `_repair_and_trace`. The engine overlays non-empty model fields onto a deterministic fallback object, forcibly restores scenario ID, persona, role, stage, age, language, retrieval mode, knowledge type, channel, and variant, sets attack type from channel/variant, attaches traces, clears safe indicators for fake cases, clears malicious cues for real cases, fills required cue categories, validates the Pydantic schema, and falls back to a schema-safe object if repair fails.

Consequently, `used_live_llm=true` means a parseable live response contributed to the final object. It does not mean the stored object is untouched model output. Near-perfect control adherence and contradiction rates partly measure the post-processing design.

### Runtime Metadata Audit

{runtime_table}

Across all rows, RAG runtime status is present for 1,019 rows and absent for 421. Of the status-bearing rows, 899 record `indexed=true` and 120 record `indexed=false`. These records support the use of the quality-profile Chroma path in most retained metadata, but they do not prove an identical backend state for every merged row. Prompt-version metadata is also incomplete outside the separate Prompt-only engine. Final publication should archive prompts and runtime manifests per row or per homogeneous run.

[[FIGURE:figures/recovery_provenance.png|Figure 6. Distribution of the 649 live-recovery replacements across model and method cells.]]

## 9. Evaluation Layers

Layer 1 validates PSQ-SCO through HermiT, SPARQL, bounded completeness, and mapping checks. Layer 2 evaluates each generated scenario for parseability, schema completeness, frozen-control adherence, required concepts, trace completeness, ontology-scope evidence, and contradiction. Layer 3 compares methods over matched model/case blocks and adds bootstrap intervals, paired tests, factor summaries, timing, error counts, and diversity diagnostics.

[[FIGURE:figures/psq_three_layer_evaluation.png|Figure 7. Three-layer evaluation architecture.]]

## 10. Ground Truth and Validation Oracles

The frozen case manifest is the reference for role, age, stage, channel, variant, difficulty, expected attack type, and safe response. The ontology is the normative reference for CQ1-CQ4 template, structure, quality-control, and evidence obligations. The output schema is the reference for executable fields.

Required-concept precision/recall uses a project-defined oracle assembled from case controls, generic fake/real requirements, and, for the direct packet method, packet must-include and evidence terms. Matching uses token overlap. It is not a human-annotated concept gold standard.

Grounding completeness uses the presence of six source/provenance trace categories. It does not verify that scenario claims are entailed by retrieved text. Ontology semantic scope checks evidence of packet/text structures, controls, and non-contradiction. It is not a trained EL embedding.

There is no completed expert gold standard for usability, pedagogy, cultural suitability, factual faithfulness, or deployability. Prompt-only precision/recall is not expected to equal 1.0 because the prompt output is a candidate evaluated against an independent case-derived concept set; the baseline is not used as its own reference.

## 11. Metric Definitions and Validity Status

| Metric | Formula or rule | Standard status | Valid interpretation | Main limitation |
| --- | --- | --- | --- | --- |
| JSON validity | 1 if a scenario object is parseable, else 0; mean is pass rate | Standard binary pass-rate idea | Parseability/executable object presence | Does not measure content quality |
| Schema completeness | `max(0, 1 - missing/8)` over required field groups | Project operationalization | Presence of required game and evidence fields | Denominator and field set need human justification |
| Control adherence | matched frozen controls / 8 | Project operationalization of accuracy | Preservation of requested labels and safe response | Strongly affected by deterministic rebinding |
| Concept precision/recall/F1 | Standard P/R/F1 over heuristic concept sets | Standard formula, project oracle | Relative concept coverage | Token matcher and required set are not human validated |
| Grounding completeness | present trace categories / 6 | Project operationalization | Trace/provenance completeness | Not factual support or entailment |
| Ontology semantic scope | `0.60 structure + 0.25 control + 0.15 non-contradiction` | Project-defined diagnostic | Presence of ontology-route evidence | Not an EL embedding or semantic reasoner score |
| Contradiction | Rule-based 0/1 flag | Project rule set | Serious internal/channel/variant inconsistency | Repair suppresses many detectable errors |
| Overall conformance | Weighted five-component index | Author-defined index | Compact operational summary | Coefficients are not human/learner calibrated |
| Embedding Diversity | `1 - mean pairwise cosine` using LaBSE | Common semantic-diversity pattern | Relative semantic separation | Encoder/set dependent; no universal threshold |
| Self-BLEU | Mean BLEU of each scenario against the rest | Established diversity diagnostic | Lexical redundancy; lower is better | Does not measure quality or semantic originality |
| Bootstrap CI | 1,000 resamples with fixed seed | Standard resampling method | Uncertainty around method mean | Assumes resampling unit matches inferential design |
| Wilcoxon signed-rank | Paired method differences | Standard nonparametric test | Distributional paired difference | Requires multiplicity adjustment and effect size |
| Friedman test | Four repeated methods per model/case block | Standard omnibus test | At least one method differs | Does not identify which pairs differ |

The code contains heuristic verbal labels for diversity values, but those cut points are not externally calibrated. This report does not use them as acceptance thresholds.

## 12. Overall-Conformance Coefficients

The implemented index is:

`Q = 0.20(JSON) + 0.25(Control) + 0.25(Concept F1) + 0.20(Grounding) + 0.10(Non-contradiction)`

Schema completeness and ontology semantic scope are reported but are not included in `Q`. The coefficients are not imported from a completed external statistical calibration and are not fitted to PersonaShield Quest expert judgments or learner outcomes. They are author-defined design coefficients and must be labeled that way.

{contribution_table}

JSON validity contributes 0.20 to every method. Control adherence contributes approximately 0.25 to every method. Non-contradiction contributes 0.10 to three methods and 0.0997 to ontology-to-text. Therefore 54.97 to 55.00 percentage points of the final index are nearly fixed. Most method separation comes from required-concept F1 and grounding trace completeness. This explains why ontology methods score highly: both have grounding=1.0, and the direct packet also has the highest concept F1.

[[FIGURE:figures/weighted_component_contributions.png|Figure 8. Contribution of each weighted component to the reported overall score.]]

### Weight-Robustness Analysis

{sensitivity_table}

The top-method ordering remains unchanged under current, equal, concept-heavy, and grounding-heavy diagnostic schemes. In 100,000 random non-negative unit-sum weight vectors sampled from `Dirichlet(1,1,1,1,1)`, Ontology packet+Prompt+RAG is top in 99,996 draws; Prompt-only is top in four extreme control-dominant draws. This shows ranking robustness for this component table. It does not justify the absolute coefficients or establish construct validity.

[[FIGURE:figures/weight_sensitivity.png|Figure 9. Sensitivity of method scores to four transparent diagnostic weight schemes.]]

## 13. Main Method Results

{method_table}

[[FIGURE:figures/method_results.png|Figure 10. Method-level component and composite means.]]

Ontology packet+Prompt+RAG leads overall conformance, concept F1, grounding, and ontology scope. Ontology-to-text has perfect mean schema and grounding and strong ontology scope, but its concept precision of 0.2701 produces an F1 of 0.3991. Its recall is high at 0.8094, indicating broad inclusion but poor selectivity under the heuristic matcher. Prompt+RAG improves schema and grounding over Prompt-only, but concept precision falls from 0.3821 to 0.3181.

The result should not be summarized as “ontology makes every quality dimension better.” The direct packet is strongest under the implemented controls. Ontology-to-text improves traceability and relative diversity but loses concept precision and includes the only detected contradiction.

## 14. Model-by-Method Results

{model_table}

[[FIGURE:figures/model_method_heatmap.png|Figure 11. Overall conformance for each model-method cell.]]

The highest cell is Qwen3 8B with Ontology packet+Prompt+RAG at 0.9015. The direct packet ranks first within all three models: Mistral 0.8774, Qwen2.5 0.8791, and Qwen3 0.9015. This cross-model consistency supports a method-level pattern. It does not isolate model capacity, because prompt lengths, recovery provenance, and runtime metadata differ across cells.

## 15. Factor Analysis

{factor_table}

The direct ontology packet has relatively small age and role ranges, while channel variation is larger. Prompt+RAG has the largest stage range at 0.0774 and channel range at 0.0554. The external corpus is heavily email-dominant, and Prompt+RAG's highest channel mean is email (0.8538) while its lowest is voice (0.7984), which is consistent with a corpus-coverage concern. This association is descriptive and is not a causal test of corpus imbalance.

The full factor table is exported in `derived_factor_breakdowns.csv`.

## 16. Error Analysis

{error_table}

The 360 Prompt-only rows all lack full evidence/provenance fields. Prompt+RAG reduces this to 134 rows but does not eliminate it. Both ontology methods reach full grounding and schema/provenance completeness under the implemented checks. Wrong-channel, wrong-attack, and unsafe-action counts are zero in all conditions, but these results must be read alongside the deterministic repair layer.

The strict “missing required concepts” flag means recall is below 1.0, not that no required concept exists. It affects every direct-packet row because the packet expands the required set with many must-include and evidence terms. Continuous precision, recall, and F1 are more informative than this binary flag.

## 17. Paired Statistical Analysis

The Friedman omnibus test reports statistic 677.1264 over 360 matched blocks with p=1.913e-146. Pairwise Wilcoxon tests use model+case matched observations. The source report did not apply multiple-comparison adjustment; this derived report applies Holm adjustment to the six p-values. Every pair remains statistically distinguishable.

{corrected_pair_table}

The source JSON field named `rank_biserial_effect_size` is not rank-weighted: it counts positive and negative differences and is a sign-dominance statistic. This report recomputes matched-pairs rank-biserial correlation from signed rank sums and retains both columns. The evaluator should rename or correct its field before the next official run.

McNemar tests are uninformative here because the binary outcome is contradiction-free status, which is nearly constant. Cochran Q was not run because statsmodels was not installed. Neither omission affects the continuous-score Friedman/Wilcoxon results, but binary “pass” claims should not be made from McNemar in this dataset.

## 18. Diversity and Repetition

{diversity_table}

[[FIGURE:figures/diversity_results.png|Figure 12. Method-level semantic and lexical diversity diagnostics.]]

Ontology packet+Prompt+RAG has the highest mean Embedding Diversity at 0.2339 and the lowest Self-BLEU at 0.7906. Ontology-to-text is close at 0.2307 and 0.8059. Prompt-only is clearly most repetitive at 0.1865 and 0.8846.

The absolute values remain weak. Mean cosine similarities of 0.7661 to 0.8135 indicate strong semantic overlap, and Self-BLEU of 0.7906 to 0.8846 indicates substantial lexical reuse. There is no literature-independent threshold that makes 0.2339 “acceptable.” Report only relative improvements until human duplicate judgments or task-specific thresholds are available.

At model-method level, the best semantic diversity is Qwen2.5 with the direct packet at 0.2485; the best Self-BLEU is Qwen3 with the direct packet at 0.7039. Mistral ontology-to-text has Self-BLEU 0.8697, showing that ontology text does not automatically solve repetition for every model.

## 19. Timing Analysis

{timing_table}

[[FIGURE:figures/timing_coverage.png|Figure 13. Direct timing and interarrival timing coverage by model-method cell.]]

Direct timing and observed interarrival timing are different measurements. Direct timing sums recorded LLM-call durations. Interarrival timing estimates elapsed time between output timestamps. Cells with zero direct rows must not be compared numerically with direct means.

Among cells with near-complete direct telemetry, Mistral Prompt+RAG averages 146.84 seconds, Mistral Prompt-only 176.30 seconds, Mistral Ontology packet 182.94 seconds, Mistral Ontology-to-text 209.53 seconds, Qwen3 Prompt+RAG 263.73 seconds, and Qwen3 Ontology-to-text 297.63 seconds. These are local-machine pipeline observations, not model benchmark speeds.

## 20. Same-Case Worked Example

The following illustrative comparison uses Qwen3 8B and case `PSQ-SCO-120-001`: IT, Beginner Introductory, age 15-21, SMS, fake. It is an engineering inspection, not a blinded expert annotation.

{worked_table}

Prompt-only is generic but aligned to the IT role. Prompt+RAG creates a concrete MFA-reset pretext. The direct ontology packet produces the richest role/tool-linked defensive action. Ontology-to-text creates a plausible scam but drifts to a bank-account pretext that is less clearly tied to the IT workflow. All four preserve the fixed labels because the engine rebinds them. This example demonstrates why label adherence alone cannot establish scenario usability or contextual quality.

## 21. Manual Inspection Status

The final evaluation exports 24 stratified scenarios with fields for JSON validity, channel/variant fit, cyber realism, pedagogical fit, grounding plausibility, repetition, acceptability, and comments. Every human-rating field is blank. No inter-rater reliability or adjudication result exists in the frozen bundle.

Before claiming usability or practical acceptability, use at least two blinded experts, freeze the rubric, score a stratified sample, calculate agreement, adjudicate disagreements, and compare automated metrics with consensus labels. The current PCUE engine can organize P/C/U/E judgments, qualifiers, and revision decisions, but its latest 1,440-row human reference study has not been completed.

## 22. Scenario Generation Versus Question Generation

The scenario is the grounded workplace event and complete game state. Questions, choices, distractors, and feedback should be generated only after the scenario is accepted. The current object includes game choices in the same generation call, but the research architecture should conceptually separate scenario validation from question/interaction validation. This prevents a valid scenario from being rejected because of a distractor defect and supports targeted revision.

## 23. TBox and ABox Interpretation

PSQ-SCO's classes, properties, and general constraints provide the TBox-like control scope. Templates, evidence records, and generated scenarios behave as ABox-like individuals/assertions. The objective is not to copy ontology individuals as the universe of stories. It is to generate diverse new instances that remain within required class/property constraints and evidence boundaries.

The current direct packet is a deterministic TBox/ABox control summary. The ontology-to-text method exposes selected record descriptions and graph traces. Both still rely on a local LLM for prose realization. Diversity results show that more work is needed to expand instance variety without violating the control scope.

## 24. Direct Answers to the Adviser Comments

1. Purpose: this is a matched evaluation of four knowledge-delivery mechanisms for local LLM serious-game scenario generation.
2. Conditions 3 and 4: Method 3 directly injects structured ontology records; Method 4 injects selected ontology verbalizations and graph-derived traces.
3. Representation: source is OWL 2/RDF XML; runtime representations are Python/JSON packet data or generated text documents.
4. Text corpus: 324 ontology record documents plus dynamic case-specific trace/walk documents; external RAG has 28,728 indexed documents.
5. RAG: Chroma PersistentClient, cosine HNSW, one-record-per-document, metadata filtering, one requested external example, no explicit reranker or threshold, embedding model not explicitly frozen.
6. Diagrams/examples: this report contains the four-mode diagram and a same-case example.
7. Final data: the report uses one frozen live-recovered bundle and one no-BERTScore evaluation run.
8. Conformance: compliance with the case, schema, concept oracle, trace obligations, and contradiction rules.
9. Composite: author-defined; component contributions and sensitivity are reported; it is not a standard human-quality score.
10. Usability: not established; automated diagnostics and one illustrative inspection are available, but expert ratings are pending.
11. Diversity: relative improvement is shown; no absolute acceptance claim is made.
12. Confounds: prompt lengths, recovery provenance, metadata coverage, and local runtime differ; findings are pipeline-level.
13. Freeze: ontology, generated bundle, evaluator, and result paths are fixed in Section 2.
14. Paper narrative: problem, methods, reproducibility, metrics, results, example, and limitations are all documented.
15. Custom metrics: each construct, formula, and limitation is specified; expert validation remains future work.
16. New reviewer: all project-specific terms are defined in this report.
17. Foundations: terminology is tied to OWL, RAG, GraphRAG, diversity, and calibrated-rubric literature.
18. GraphRAG: the method is renamed ontology-to-text RAG context; it is not Microsoft GraphRAG.
19. Time: no additional generation experiment is required for this report; the next priority is human review and writing.
20. Education: content-quality claims are separated from learning-outcome claims; learner validation is a next study.

## 25. Threats to Validity

### Construct Validity

Overall conformance, grounding completeness, ontology scope, schema completeness, and concept extraction contain project-defined choices. The composite coefficients and qualifier thresholds are not psychometrically calibrated. Human P/C/U/E judgments are missing.

### Internal Validity

Final rows combine original and recovery runs. Prompt-only uses a separate engine for major cells. Prompt lengths, model token budgets, metadata completeness, and RAG retrieval success are not fully homogeneous. Deterministic post-processing suppresses control and contradiction failures.

### External Validity

The RAG corpus is email- and English-dominant. Only three local 7B/8B model profiles are tested. Scenarios assume one primary channel and variant, although real attacks may combine email, SMS, and voice.

### Statistical Conclusion Validity

The paired design and large differences make method effects clear for the implemented index. Nevertheless, the original effect-size field was mislabeled, original pairwise p-values were unadjusted, timing coverage is heterogeneous, and 120 cases are not independent learner observations.

### Ecological and Educational Validity

No learner played these scenarios in the reported experiment. No learning gain, retention, transfer, engagement, or instructor workflow outcome was measured. Content conformance must not be described as educational effectiveness.

## 26. Claims Matrix

| Claim | Status | Evidence |
| --- | --- | --- |
| PSQ-SCO v9.1 is logically consistent under the recorded HermiT run | Supported | PASS, 0 unsatisfiable classes |
| CQ1-CQ4 required checks are present | Supported within bounded scope | 4,362/4,362 checks; 8/8 ASK tests |
| All final outputs are live LLM rows | Supported as pipeline metadata | 1,440/1,440; 0 fallback after recovery |
| Direct ontology packet improves automated conformance | Supported for this dataset/index | +0.1119 vs Prompt-only; Holm-adjusted paired p remains significant |
| Ontology guidance eliminates trace-field incompleteness | Supported under implemented trace checker | 0 missing-evidence rows in both ontology methods |
| Ontology guidance improves diversity | Supported relatively, not absolutely | Higher Embedding Diversity/lower Self-BLEU than Prompt-only |
| Scenarios are usable and deployable | Not established | Human review fields blank |
| Scenarios improve learning | Not tested | No learner outcomes |
| Method 4 is GraphRAG | Rejected | Actual code uses ontology verbalization/in-memory selection, not GraphRAG indexing/search |
| Coefficients are empirically optimal | Not established | Sensitivity exists; no human/learner calibration |

## 27. Required Next Actions

1. Complete blinded expert review of the exported sample and calculate inter-rater agreement.
2. Archive exact prompts, model options, Chroma version/default embedding model, corpus hashes, and per-run runtime manifests.
3. Correct the effect-size field and add Holm adjustment in the evaluator itself.
4. Separate raw LLM output, deterministic rebinding, repair, and final output in the data model.
5. Add factual-grounding judgments that test support in retrieved source text.
6. Treat component metrics as primary and the composite as secondary until calibrated.
7. Expand voice, SMS, Thai, and multi-channel evidence.
8. Separate scenario acceptance from question/distractor acceptance.
9. Run PCUE human calibration and later learner-outcome validation.

## 28. Reproducibility Artifacts

All original result files remain in `{EVAL_DIR}`. This report adds the following derived, non-destructive artifacts in `{OUT_DIR}`:

- component contributions and alternative weight scores;
- 100,000-vector random weight robustness summary;
- leave-one-component-out analysis;
- corrected matched rank-biserial and Holm-adjusted pairwise table;
- role/channel/variant/stage/age breakdowns;
- dataset-balance table;
- runtime and prompt-metadata audit;
- recovery distribution;
- same-case four-mode example;
- slide-ready core-data sheet with claim boundaries;
- SHA-256 manifest for the frozen ontology, scenario JSONL files, and core evaluation inputs.

## 29. Academic and Technical Sources

1. W3C. [OWL 2 Web Ontology Language Overview](https://www.w3.org/TR/owl2-overview/).
2. W3C. [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/).
3. Glimm et al. (2014). [HermiT: An OWL 2 Reasoner](https://doi.org/10.1007/s10817-014-9305-1).
4. Lewis et al. (2020). [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html). NeurIPS.
5. Edge et al. (2024). [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130).
6. Jin et al. (2024). [Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs](https://arxiv.org/abs/2404.07103). ACL.
7. Gardent et al. (2017). [The WebNLG Challenge: Generating Text from RDF Data](https://aclanthology.org/W17-3518/).
8. Reimers and Gurevych (2019). [Sentence-BERT](https://arxiv.org/abs/1908.10084). EMNLP-IJCNLP.
9. Feng et al. (2022). [Language-agnostic BERT Sentence Embedding](https://aclanthology.org/2022.acl-long.62/). ACL.
10. Zhu et al. (2018). [Texygen](https://arxiv.org/abs/1802.01886). SIGIR.
11. Tevet and Berant (2021). [Evaluating the Evaluation of Diversity in Natural Language Generation](https://aclanthology.org/2021.eacl-main.25/). EACL.
12. Hashemi et al. (2024). [LLM-Rubric](https://aclanthology.org/2024.acl-long.745/). ACL.
13. Sokolova and Lapalme (2009). [A Systematic Analysis of Performance Measures for Classification Tasks](https://doi.org/10.1016/j.ipm.2009.03.002).
14. Wilcoxon (1945). [Individual Comparisons by Ranking Methods](https://doi.org/10.2307/3001968).
15. Friedman (1937). [The Use of Ranks to Avoid the Assumption of Normality](https://doi.org/10.1080/01621459.1937.10503522).
16. Holm (1979). [A Simple Sequentially Rejective Multiple Test Procedure](https://www.jstor.org/stable/4615733).
17. Efron (1979). [Bootstrap Methods](https://doi.org/10.1214/aos/1176344552).

Venue quartiles and rankings change by year and database. Verify required Q1/Q2/Q3 classifications immediately before publication rather than embedding unverified static rankings.
"""

    analysis_report = f"""# Research Analysis and Complete Adviser-Comment Response

Version 1.0 | Based on the frozen 1,440-row live-recovered experiment | 14 July 2026

## Core Interpretation

The experiment demonstrates that ontology-derived controls can improve an automated scenario-generation pipeline, but the mechanism and claim must be stated precisely. The strongest tested method is not GraphRAG. It is direct injection of a structured semantic packet selected from the local PSQ-SCO RDF/XML graph, combined with external vector RAG. The ontology-to-text method is a second, distinct approach that verbalizes selected ontology records and deterministic graph traces before prompt injection.

The direct packet reaches 0.8860 on the current author-defined operational index and wins across all three models. Its advantage is driven primarily by full grounding-trace completeness and stronger required-concept F1. JSON validity, control adherence, and non-contradiction are nearly saturated because the engine repairs and rebinds outputs. The result therefore supports control/trace conformance, not independent human quality.

The most important unresolved question is practical quality. Automated diversity is better than Prompt-only but remains low in absolute terms. The same-case example exposes contextual drift that the fixed-label checker cannot detect. Human expert scoring is still blank. The correct paper posture is “promising ontology-guided pipeline evidence with explicit validation boundaries,” not “fully validated game content.”

## Comment 1: Clarify the Purpose Immediately

### Evidence-Based Answer

The presentation should open with: “This study tests whether PSQ-SCO ontology guidance improves the conformance, traceability, and diversity of locally generated cybersecurity serious-game scenarios compared with Prompt-only and vector-RAG baselines.”

The object is a structured scenario artifact, not learner performance. The primary comparison is four generation pipelines over the same 120 case specifications and three local models.

### Status

Resolved in the report structure and presentation brief. Do not begin with ontology counts or architecture before stating the problem and comparison.

## Comment 2: Differentiate Conditions 3 and 4

### Evidence-Based Answer

Condition 3 parses the OWL/RDF XML and creates a structured Python/JSON semantic packet containing selected templates, rules, evidence, quality controls, must-include terms, must-exclude terms, validation checks, and provenance. The packet is inserted directly into the prompt.

Condition 4 creates 324 static ontology record verbalizations and, for each case, selects relevant records by deterministic in-memory scoring. It adds a Graph-CoT-inspired reasoning-interaction-execution document and a selected-subgraph walk. These text documents enter the prompt through the RAG-context structure.

### Status

Resolved conceptually. The remaining engineering improvement is to archive one exact prompt/context example for all four methods.

## Comment 3: State Ontology Representation and Conversion

### Evidence-Based Answer

The authoritative source is `personashield-psq-sco-v9.1.owl`, serialized as RDF/XML. The generator uses Python `xml.etree.ElementTree`, extracts each `rdf:Description`, local identifier, RDF types, labels, definitions/comments, and property values, and stores 324 compact `OntologyRecord` objects.

Method 3 converts selected records into a structured semantic packet. Method 4 converts records into plain text containing identifier, RDF types, label, definition, and selected property-value relations. Dynamic text adds the selected route and control summary.

### Status

Resolved. Do not call the source Turtle or JSON-LD. Do not call the ontology itself “JSON”; only the runtime packet is JSON-like structured data.

## Comment 4: Define the Text-RAG Corpus

### Evidence-Based Answer

There are two distinct corpora. The external RAG corpus contains 28,728 indexed documents after caps and deduplication. The ontology-text corpus contains 324 static record documents and dynamic case-specific trace/walk documents.

The external corpus is shared by Prompt+RAG, Ontology packet+Prompt+RAG, and Ontology-to-text+Prompt+RAG. Prompt-only has no retrieval. Ontology text is not inserted into Chroma; it is selected in memory by the ontology module and then combined with external context.

### Status

Resolved in this report. The paper must maintain the external/ontology corpus distinction.

## Comment 5: Report Full RAG Configuration

### Evidence-Based Answer

The current configuration uses Chroma PersistentClient, cosine HNSW, one JSONL row per document, exact lowercase-text deduplication, profile caps, candidate retrieval of `max(16 x requested_n, 64)`, metadata filters, and fallback ladders. One external example is requested in the final compact runs. No explicit reranker or similarity threshold is implemented.

The exact embedding model is not fixed because the code accepts Chroma's installed default. This must be corrected for full reproducibility. Runtime status is missing for 421 final rows because the merged dataset combines historical and recovery records.

### Status

Partially resolved. Configuration is documented, but exact embedding-model version, package versions, corpus hashes, prompt hashes, and homogeneous row-level runtime manifests remain required.

## Comment 6: Use Diagrams and Worked Examples

### Evidence-Based Answer

The reporting bundle includes architecture, four-method, ontology-validation, experiment-design, metric, recovery, diversity, corpus-balance, and timing figures. It also includes Qwen3 case 001 across all four methods.

The example shows why qualitative evidence is necessary: ontology-to-text preserves IT/SMS/fake labels but writes a bank-account pretext with weaker IT-workflow alignment. This defect is not visible in fixed-label adherence.

### Status

Resolved for reporting. A final paper should include one compact four-column example and move longer text to an appendix.

## Comment 7: Recheck and Freeze Preliminary Results

### Evidence-Based Answer

The frozen generation bundle is `{GEN_DIR}`. It contains 1,440 live rows, zero remaining fallback rows, and 649 replacements. The frozen no-BERTScore evaluation is `{EVAL_DIR}`.

Every model has 120 complete cases in every method. All numbers in this bundle are recomputed or read from those paths; no older fallback-containing report is used.

### Status

Resolved. Additional generation should not be mixed into this study without a new protocol/version.

## Comment 8: Define Conformance and Its Reference

### Evidence-Based Answer

Conformance is an operational index combining parseability, frozen-control preservation, heuristic required-concept F1, evidence/provenance trace completeness, and absence of rule-detectable contradiction. Its references are the frozen case manifest, output schema, project-required concept oracle, evidence trace fields, and contradiction rules.

It is not conformance to human preferences, learning outcomes, or all ontology axioms. “Strongest conformance” means highest mean on this named project index.

### Status

Resolved in terminology. Rename it in the paper as “automated operational conformance index” rather than generic “quality.”

## Comment 9: Justify the Composite and Weights

### Evidence-Based Answer

The coefficients are author-defined and not taken from a completed external calibration study. The report therefore exposes every component, shows exact weighted contributions, evaluates equal/concept-heavy/grounding-heavy alternatives, samples 100,000 random unit-sum weight vectors, and performs leave-one-component-out analysis.

The direct packet remains top under all four stated schemes and 99.996% of random weight draws. This supports ranking robustness, not coefficient validity. Exact coefficients still require expert/learner calibration on separate training and test sets.

### Status

Partially resolved. Sensitivity addresses “does the conclusion depend on these numbers?” but does not answer “are these the correct normative weights?” Human calibration remains required.

## Comment 10: Evaluate Usability and Practical Quality

### Evidence-Based Answer

Current automatic checks establish executable structure, traceability, and selected consistency rules. They do not establish whether a learner understands the scenario, whether choices are pedagogically effective, or whether an instructor would deploy it.

The PCUE architecture defines Pedagogical Quality, Cybersecurity Realism, Usability/Game Clarity, and Ethical Safety, but the final human worksheet is blank. No acceptance rate should be reported as a human-validated result.

### Status

Open. Complete blinded expert PCUE review and adjudication.

## Comment 11: Interpret Diversity Cautiously

### Evidence-Based Answer

The highest method mean Embedding Diversity is 0.2339 and the lowest method mean Self-BLEU is 0.7906, both for the direct packet. These are improvements relative to Prompt-only (0.1865 and 0.8846), but they still indicate high semantic and lexical overlap.

No universal threshold makes 0.2339 acceptable. Values depend on LaBSE, the serialized scenario text, set composition, and grouping. Report relative comparisons and inspect high-similarity pairs.

### Status

Resolved in interpretation; practical diversity remains an open quality problem.

## Comment 12: Separate Model, Prompt, Retrieval, and Pipeline Effects

### Evidence-Based Answer

The matched case IDs control scenario requirements, but the final data do not perfectly hold prompt length, engine version, token limits, retrieval success, and recovery provenance constant. Qwen Prompt-only uses a separate engine. Some rows lack generation metadata. External RAG returns zero examples for a nontrivial subset.

The correct causal wording is pipeline-level: “Under the completed PersonaShield Quest pipelines, ontology-packet conditions scored higher.” A clean causal ablation would need one engine version, archived prompts, fixed decoding settings, identical retrieval availability, and preferably repeated seeds.

### Status

Resolved as a limitation, not resolved experimentally.

## Comment 13: Stop Expanding and Freeze the Study

### Evidence-Based Answer

The ontology, final generation folder, evaluation folder, model set, case set, metric set, and BERTScore-disabled configuration are frozen. This report adds only derived analyses from existing rows.

### Status

Resolved. The next work is human validation and manuscript writing, not adding another automatic metric.

## Comment 14: Build the Paper From Problem to Evidence

### Evidence-Based Answer

Recommended order: serious-game content problem; ontology/RAG gap; research questions; PSQ-SCO scope; matched design; exact four methods; dataset and runtime; metric construct table; results; qualitative example; threats; educational implications; conclusion.

### Status

Resolved in the evaluation report and presentation brief.

## Comment 15: Custom Metrics Require Validation

### Evidence-Based Answer

This bundle labels standard formulas separately from project-specific oracles and weights. It defines range, computation, reference, and limitation for every metric. Grounding completeness is explicitly trace completeness, ontology scope is explicitly a project diagnostic, and overall conformance is explicitly an author-defined index.

Validation requires correlations with blinded expert ratings, known-good/known-bad scenarios, sensitivity/specificity analysis, and threshold calibration. Formula documentation alone is not validation.

### Status

Partially resolved through definition and sensitivity. Criterion validity remains open.

## Comment 16: Write for a Reviewer New to the Project

### Evidence-Based Answer

The reports define PersonaShield Quest, PSQ-SCO, macro/micro stage, frozen case, semantic packet, external RAG, ontology-to-text context, TBox/ABox, all metrics, and all decision boundaries at first use.

### Status

Resolved in the new reporting structure.

## Comment 17: Strengthen Conceptual Foundations

### Evidence-Based Answer

The report grounds OWL/HermiT/SPARQL in W3C and reasoner sources; RAG in Lewis et al.; GraphRAG in Edge et al./Microsoft; graph-to-text in WebNLG; graph reasoning in Graph-CoT; diversity in Sentence-BERT/LaBSE, Texygen, and Tevet/Berant; rubric calibration in LLM-Rubric.

It also states where the implementation differs from the cited method, which is more important than borrowing a label.

### Status

Resolved for the core terms. Publication references and venue metadata should still be independently verified.

## Comment 18: Do Not Mislabel the Method as GraphRAG

### Evidence-Based Answer

The implementation does not build an entity/community graph from the RAG corpus, generate community reports, or perform local/global graph search. It verbalizes an existing ontology and selects context deterministically. The title and method name should use “ontology-to-text RAG context” or “ontology-guided RAG,” with a precise implementation description.

### Status

Resolved. “GraphRAG” should be removed unless a future system materially implements graph-structured indexing/retrieval.

## Comment 19: Manage Time and Finish the Writing

### Evidence-Based Answer

The automatic experiment is frozen. Remaining tasks are bounded: expert annotation, two metric corrections, reproducibility archive, manuscript revision, and adviser review.

### Status

Resolved as a project-management decision.

## Comment 20: Strengthen Engineering-Education Motivation

### Evidence-Based Answer

The educational value proposition is a controlled content supply for adaptive cybersecurity practice: role-relevant situations, staged cognitive demand, safe decision rehearsal, explanatory feedback, and auditable scenario revision. The current study validates content-pipeline properties, not learning.

The next educational study should measure pre/post knowledge, normalized gain where appropriate, delayed retention, decision errors, hint use, time-on-task, transfer scenarios, and perceived clarity. Scenario quality should be treated as an instructional-material mediator rather than equated with learning outcomes.

### Status

Conceptually resolved; learner evidence remains future work.

## Integrated Result Analysis

### Why the Direct Packet Wins

It receives full trace credit and a compact, explicit constraint representation. Its concept F1 is 0.5447, higher than all other methods. Ontology-to-text has higher recall (0.8094) but much lower precision (0.2701), indicating a verbose or diffuse concept footprint under the heuristic matcher. Direct structure appears easier for small local models to use selectively than multiple verbalized ontology documents.

### Why Prompt+RAG Helps but Does Not Lead

Prompt+RAG raises grounding from 0.4810 to 0.7824 and schema completeness from 0.8750 to 0.9535. Its concept F1 falls to 0.4480. Retrieved examples increase evidence coverage but can add irrelevant concepts or fail metadata filters. The corpus is also strongly email- and English-dominant.

### Why Ontology-to-Text Is Second

It obtains full schema and grounding and strong ontology scope at 0.8641. Its high recall suggests broad ontology-content presence, but low precision suppresses F1. One contradiction occurs. It also creates longer context and slower direct timing in available cells. This method may be useful when auditable graph-derived context is the research objective, but the current direct packet is more efficient and selective.

### Model Interpretation

Qwen3 gains most from the direct packet and reaches 0.9015. Mistral is weakest on Prompt-only but narrows the gap with RAG. Model rankings change by method, so there is no single universally best model. The stable observation is that the direct packet is best within each model.

## Qualitative Case Analysis

{worked_table}

The direct packet example uses MFA, organization tools, and a trusted verification route. Prompt+RAG supplies a concrete suspicious URL and MFA pretext. Prompt-only is generic. Ontology-to-text shifts to a bank-account scam. The fixed labels stay correct in all four, demonstrating a construct gap between metadata conformance and contextual scenario quality.

## Coefficient Analysis

{contribution_table}

The index awards nearly fixed credit for parseability, repaired controls, and non-contradiction. This makes grounding and concept F1 the decisive dimensions. The direct-packet lead is robust to many weights because it weakly or strongly dominates competing methods on most included components. Absolute score interpretation remains unsupported: 0.8860 is not “88.6% quality” and is not an acceptance probability.

## Corrected Statistical Interpretation

{corrected_pair_table}

All Holm-adjusted pairwise results remain significant. Corrected rank-biserial effects show a very strong direct-packet advantage over Prompt-only and Prompt+RAG, a strong advantage over ontology-to-text, and a moderate ontology-to-text advantage over Prompt+RAG. Statistical strength applies to the implemented index and matched cases, not to unmeasured learner benefit.

## Recommended Paper Title

“Ontology-Guided Local LLM Scenario Generation for Cybersecurity Serious Games: A Matched Comparison of Prompting, Vector RAG, Structured Ontology Packets, and Ontology-to-Text Context”

Avoid “GraphRAG” in the title.

## Recommended Research Questions

1. How does a structured PSQ-SCO semantic packet affect automated scenario conformance relative to Prompt-only and external vector RAG?
2. How does ontology-to-text context affect grounding, ontology-scope evidence, and required-concept coverage?
3. How do the four methods differ in semantic and lexical diversity across matched cases?
4. Are method patterns consistent across Qwen2.5 7B, Qwen3 8B, and Mistral 7B?
5. What implementation, corpus, and post-processing factors limit the interpretation of automated results?

Usability and learning effectiveness should be future human/learner questions unless the required data are collected before submission.

## Recommended Main Claim

“Across 360 matched outputs per method, direct PSQ-SCO semantic-packet guidance achieved the highest mean automated operational conformance (0.8860), exceeding Prompt-only by 0.1119 and external Prompt+RAG by 0.0679. The method ranking was consistent across three local open-weight models and robust to transparent alternative coefficient schemes. Both ontology-guided methods achieved complete evidence/provenance trace fields under the implemented checker. However, diversity remained limited and human usability/educational validation was not completed; results should therefore be interpreted as pipeline-level conformance evidence rather than proof of deployable instructional quality.”

## Manuscript Red Lines

- Do not say GraphRAG.
- Do not call 0.8860 a percentage of quality.
- Do not claim usability, acceptance, or learning gain without human/learner data.
- Do not describe grounding completeness as factual grounding.
- Do not call ontology scope an EL embedding.
- Do not hide the deterministic repair/rebinding stage.
- Do not compare direct and interarrival timing as if identical.
- Do not present diversity values as meeting a universal threshold.
- Do not claim the exact weights are externally validated.

## Final Readiness Assessment

| Area | Status | Required action |
| --- | --- | --- |
| Ontology formal validation | Complete for recorded CQ1-CQ4 scope | Correct auxiliary HermiT path metadata |
| Matched generation set | Complete, 1,440 live rows | Archive prompt/runtime manifests and hashes |
| Automated evaluation | Complete with derived corrections | Implement effect-size rename/correction and Holm in code |
| Method terminology | Corrected | Use ontology packet and ontology-to-text labels consistently |
| Diversity analysis | Complete as diagnostic | Add human duplicate review |
| Practical usability | Incomplete | Complete blinded PCUE/expert review |
| Learning effectiveness | Not tested | Separate learner study |
| Publication narrative | Ready for drafting | Use claims and red lines above |

## Sources

1. [Microsoft GraphRAG overview](https://microsoft.github.io/graphrag/query/overview/).
2. [Edge et al., From Local to Global](https://arxiv.org/abs/2404.16130).
3. [Lewis et al., Retrieval-Augmented Generation](https://papers.nips.cc/paper_files/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).
4. [Jin et al., Graph Chain-of-Thought](https://arxiv.org/abs/2404.07103).
5. [Tevet and Berant, Evaluating Diversity Evaluation](https://aclanthology.org/2021.eacl-main.25/).
6. [Hashemi et al., LLM-Rubric](https://aclanthology.org/2024.acl-long.745/).
7. [OWL 2 Overview](https://www.w3.org/TR/owl2-overview/).
8. [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).
"""

    presentation_brief = f"""# Presentation Core Evidence Brief

Version 1.0 | Slide-ready evidence from the frozen PersonaShield Quest experiment | 14 July 2026

## Presentation Objective

Use this one sentence first:

“This presentation evaluates whether PSQ-SCO ontology guidance improves the conformance, traceability, and diversity of locally generated cybersecurity serious-game scenarios compared with Prompt-only and vector-RAG baselines.”

Do not begin with ontology size, equations, or implementation history.

## Slide 1: Research Problem

### Headline

AI can generate scenario prose, but game deployment requires controlled role, stage, channel, fake/real, safety, evidence, and executable structure.

### Core Data

- Full design space: `5 roles x 9 stages x 5 ages x 3 channels x 2 variants = 1,350 slots`.
- Current experiment evaluates scenario artifacts, not learners.

### Speaker Note

The contribution is a controlled content pipeline and its matched evaluation, not a generic chatbot.

## Slide 2: Study Question and Frozen Design

### Headline

The same 120 input specifications are generated by every method and every model.

### Core Data

- 30 base groups = 3 channels x 2 variants x 5 roles.
- 90 difficulty-anchor cases + 30 balanced repetitions = 120.
- 120 x 3 models x 4 methods = 1,440 outputs.
- All model-method cells have exactly 120 case IDs.

### Visual

Use `figures/psq_paper120_design.png`.

## Slide 3: Four Methods

### Headline

The methods differ in how knowledge is delivered to the same scenario-generation task.

### Core Data

1. Prompt-only: case/persona/schema; no retrieval or ontology.
2. Prompt+RAG: external Chroma text retrieval.
3. Ontology packet+Prompt+RAG: direct structured template/rule/evidence packet.
4. Ontology-to-text+Prompt+RAG: selected ontology verbalizations and graph-derived trace/walk text.

### Visual

Use `figures/psq_four_modes.png`.

### Do Not Say

Do not call Method 4 Microsoft GraphRAG.

## Slide 4: Exact Difference Between Methods 3 and 4

### Headline

Method 3 sends structure; Method 4 sends selected ontology-derived text.

### Core Data

- Method 3 runtime selection: local RDF/XML subgraph filtering.
- Method 4 static text corpus: 324 record documents.
- Method 4 final case context: four ontology text documents where metadata is retained.
- SPARQL validates the ontology but does not construct each generation packet.
- Ontology text is selected in memory and is not inserted into the Chroma index.

## Slide 5: Ontology Evidence

### Headline

PSQ-SCO v9.1 passes formal and CQ-bounded validation.

### Core Data

- Release count: 73 classes, 49 object properties, 39 data properties, 133 individuals, 3,229 triples.
- HermiT: consistent, zero unsatisfiable classes, 3.636 seconds.
- SPARQL ASK: 8/8 passed.
- Bounded completeness: 4,362/4,362 for CQ1-CQ4 only.
- Runtime mapping: 1,440/1,440.

### Visual

Use `figures/psq_ontology_validation_flow.png`.

## Slide 6: External RAG Dataset

### Headline

The external corpus is large but substantially imbalanced.

### Core Data

- 23 files; 87,661 raw rows; 29,731 after caps; 28,728 indexed; 1,003 duplicates skipped.
- Email 89.9%, SMS 7.2%, voice 2.8%.
- English 97.3%, Thai 2.7%.
- Chroma PersistentClient, cosine HNSW.
- Exact default embedding model not explicitly frozen: reproducibility limitation.

### Visual

Use `figures/rag_corpus_balance.png`.

## Slide 7: Data Recovery and Integrity

### Headline

The final report excludes fallback rows, but it combines original and recovery executions.

### Core Data

- Final rows: 1,440 live, zero fallback.
- Recovery replacements: 649.
- Mistral replacements: 350; Qwen2.5: 179; Qwen3: 120.
- Runtime/prompt metadata remains incomplete for some retained original rows.

### Visual

Use `figures/recovery_provenance.png`.

### Speaker Note

Say “final live-recovered pipeline dataset,” not “one homogeneous run.”

## Slide 8: What Each Metric Means

### Headline

Component metrics answer different questions and must not be collapsed conceptually.

### Core Data

- JSON validity: parseable scenario-object pass rate.
- Schema completeness: executable game/evidence fields present.
- Control adherence: frozen labels and safe response preserved.
- Concept P/R/F1: heuristic required concept matching.
- Grounding completeness: six trace/provenance field types present.
- Ontology scope: project diagnostic of ontology-route evidence.
- Contradiction: rule-detectable severe inconsistency.
- Embedding Diversity and Self-BLEU: set-level repetition diagnostics.

### Do Not Say

Grounding completeness is not factual entailment. Ontology scope is not a trained EL embedding.

## Slide 9: Overall Index and Coefficient Transparency

### Headline

The overall score is an author-defined operational index, not a standard quality percentage.

### Core Data

`Q = .20 JSON + .25 Control + .25 Concept F1 + .20 Grounding + .10 Non-contradiction`

- Schema and ontology scope are not included.
- Roughly 0.55 of every score is nearly fixed by saturated components.
- Main separation comes from concept F1 and grounding.
- Direct ontology remains top under four stated schemes and 99.996% of 100,000 random non-negative weight vectors.

### Visual

Use `figures/weighted_component_contributions.png` and, if time allows, `figures/weight_sensitivity.png`.

## Slide 10: Main Method Result

### Headline

The direct ontology packet is the strongest automated-conformance method.

{md_table(
    ["Method", "Overall", "Concept F1", "Grounding", "Ontology scope"],
    [[METHOD_LABEL[row.method], f4(row.overall_conformance), f4(row.required_concept_f1), f4(row.grounding_completeness), f4(row.ontology_semantic_scope)] for row in method_summary.itertuples(index=False)],
)}

### Visual

Use `figures/method_results.png`.

### Main Interpretation

Method 3 is strongest; Method 4 improves traceability but loses concept precision; external RAG improves grounding over Prompt-only.

## Slide 11: Model Comparison

### Headline

The method pattern is consistent across all three local models.

{model_table}

### Core Result

Highest cell: Qwen3 8B + direct ontology packet = 0.9015.

### Visual

Use `figures/model_method_heatmap.png`.

## Slide 12: Statistical Evidence

### Headline

Matched differences remain significant after Holm adjustment.

### Core Data

- Direct ontology - Prompt-only: +0.1119, 95% CI [0.1085, 0.1151].
- Direct ontology - Prompt+RAG: +0.0679, 95% CI [0.0624, 0.0732].
- Ontology-to-text - Prompt+RAG: +0.0309, 95% CI [0.0251, 0.0368].
- Friedman: 677.1264, p=1.913e-146.
- Corrected rank-biserial effects are reported; the legacy source field was sign dominance.

### Speaker Note

Statistical significance applies to the implemented index, not learning gain.

## Slide 13: Diversity and Duplication

### Headline

Ontology guidance improves relative diversity, but repetition remains a real limitation.

{diversity_table}

### Visual

Use `figures/diversity_results.png`.

### Do Not Say

Do not call 0.2339 acceptable without human/task calibration.

## Slide 14: One Same-Case Example

### Headline

Label conformance can hide contextual quality differences.

{worked_table}

### Main Interpretation

The direct packet gives the clearest IT/MFA/workflow grounding. Ontology-to-text drifts toward a bank scam despite preserving IT/SMS/fake labels. This motivates human review.

## Slide 15: What the Study Proves and Does Not Prove

### Supported

- PSQ-SCO is formally consistent in the recorded reasoner run.
- The direct ontology packet improves the automated operational index.
- Ontology methods complete implemented evidence/provenance trace fields.
- Method ordering is consistent across the three tested models.

### Not Yet Supported

- Human usability or deployability.
- Factual faithfulness to retrieved sources.
- Learner knowledge gain or transfer.
- Absolute diversity acceptability.
- Empirical optimality of the coefficients.

## Slide 16: Adviser Comments Resolved

### Headline

The revised reporting corrects terminology, exposes implementation details, and narrows claims.

- Purpose stated first.
- Conditions 3 and 4 operationally distinguished.
- OWL/RDF XML and transformations documented.
- Corpus, chunk unit, vector store, filters, and imbalance documented.
- Conformance reference and custom coefficients disclosed.
- GraphRAG label rejected.
- Same-case example included.
- Human usability remains explicitly open.

## Slide 17: Conclusion and Next Step

### Headline

Direct structured ontology control is the strongest tested pipeline; human validation is now the priority.

### Closing Statement

“Ontology guidance improved automated control and traceability, but safe and structurally valid generation does not by itself guarantee diverse, usable, or educationally effective game content.”

### Next Actions

1. Complete blinded expert PCUE ratings and agreement.
2. Freeze exact embedding/prompt/runtime metadata.
3. Correct effect-size and multiplicity reporting in code.
4. Add factual-grounding verification.
5. Conduct a separate learner-outcome study.

## Ninety-Second Summary

PersonaShield Quest needs 1,350 role-, stage-, age-, channel-, and variant-specific cybersecurity scenarios. We tested 120 balanced case specifications with three local open-weight LLMs and four methods, yielding 1,440 final live outputs. The direct PSQ-SCO semantic packet produced the highest automated operational conformance at 0.8860 and was best for every model. Ontology-to-text context was second, external RAG third, and Prompt-only fourth. Both ontology methods completed all implemented evidence/provenance trace fields. However, the score is author-defined, much of it is saturated by deterministic post-processing, the RAG corpus is email/English dominant, and diversity remains low. The method is ontology-to-text context, not Microsoft GraphRAG. Human expert usability and learner effectiveness have not yet been established, so the defensible contribution is an ontology-guided, local, auditable generation pipeline with clear boundaries and a completed matched evaluation.

## Likely Questions and Short Answers

### What is a 120 case?

One frozen input combination of role, stage, age, channel, and variant. The generated texts differ, but the requested case is identical across methods and models.

### Is Method 4 GraphRAG?

No. It verbalizes selected ontology records and graph traces, then injects them as text context. It does not implement Microsoft GraphRAG indexing or local/global graph search.

### Why is Prompt-only precision not 1.0?

Prompt-only is a candidate system, not the reference. Precision/recall compare generated concepts against an independent case-derived concept set.

### Is 0.8860 equal to 88.6% quality?

No. It is a weighted project index on normalized automated components.

### Are the weights validated?

No. The ranking is sensitivity-tested, but the exact coefficients still require human or learner calibration.

### Are the scenarios usable?

Not yet proven. The manual worksheet is exported but human ratings are blank.

### Does grounding completeness mean factual grounding?

No. It means required source/provenance trace categories are present.

### Why use open-weight models?

They allow local, affordable, reproducible educational experimentation without requiring paid proprietary APIs.
"""

    report_paths = {
        "FINAL_DETAILED_EVALUATION_RESULTS_REPORT.md": evaluation_report,
        "FINAL_RESEARCH_ANALYSIS_AND_ADVISOR_RESPONSE.md": analysis_report,
        "PRESENTATION_CORE_EVIDENCE_BRIEF.md": presentation_brief,
    }
    for name, content in report_paths.items():
        (OUT_DIR / name).write_text(content, encoding="utf-8")

    docx_outputs = [
        build_docx(
            OUT_DIR / "FINAL_DETAILED_EVALUATION_RESULTS_REPORT.md",
            "Final Detailed Evaluation and Results Report",
            "PSQ-SCO v9.1 and the 1,440-row four-method local-LLM experiment",
            "Final_Detailed_Evaluation_and_Results_Report.docx",
        ),
        build_docx(
            OUT_DIR / "FINAL_RESEARCH_ANALYSIS_AND_ADVISOR_RESPONSE.md",
            "Research Analysis and Adviser Response",
            "Complete evidence-based response to the methodology, terminology, metric, and presentation comments",
            "Final_Research_Analysis_and_Adviser_Response.docx",
        ),
        build_docx(
            OUT_DIR / "PRESENTATION_CORE_EVIDENCE_BRIEF.md",
            "Presentation Core Evidence Brief",
            "Slide-ready messages, numbers, visuals, speaker notes, and defensible claim boundaries",
            "Presentation_Core_Evidence_Brief.docx",
        ),
    ]

    manifest = {
        "created_at": "2026-07-14T01:22:18+09:00",
        "run_id": RUN_ID,
        "purpose": "Advisor-aligned frozen reporting bundle; no scenario regeneration or rescoring.",
        "source_generation_bundle": str(GEN_DIR),
        "source_evaluation_bundle": str(EVAL_DIR),
        "source_ontology": str(ONTOLOGY_PATH),
        "source_adviser_comments": str(ADVISER_COMMENTS_PATH),
        "source_row_count": int(len(scores)),
        "source_live_rows": int(merge_summary["live_rows"]),
        "source_fallback_rows": int(merge_summary["remaining_non_live_rows"]),
        "derived_analysis_notes": [
            "Holm-adjusted p-values and corrected matched-pairs rank-biserial correlations are post-hoc reporting corrections derived from frozen scores.",
            "Weight sensitivity is a robustness analysis, not empirical coefficient calibration.",
            "Worked example is illustrative engineering inspection, not expert annotation.",
        ],
        "markdown_reports": list(report_paths),
        "docx_reports": [path.name for path in docx_outputs],
        "derived_csvs": list(derived_files),
        "source_hash_manifest": "source_artifact_hashes.json",
        "figures": sorted(path.name for path in FIG_DIR.glob("*.png")),
    }
    (OUT_DIR / "report_bundle_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
