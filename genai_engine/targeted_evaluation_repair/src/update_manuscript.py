"""Create a separate, targeted Overleaf revision from the supplied manuscript.

The script verifies protected blocks byte-for-byte and updates only the locations
authorized by the targeted PSQ-SCO repair specification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


DEFAULT_MANUSCRIPT_SOURCE = Path(
    r"external-assets/19cedd7e-d4c8-41d6-8ecd-bc4cecbc3f7f"
    r"\pasted-text.txt"
)
DEFAULT_PACKAGE_SOURCE = Path(
    r"archived-inputs/latex"
    r"\IJCKG2026_Overleaf_Required_Files_Only"
)
DEFAULT_EVALUATION_DIR = Path(__file__).resolve().parents[1] / "evaluation_rerun"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "overleaf"

METHOD_ORDER = (
    "prompt_only",
    "prompt_rag",
    "ontology_prompt_rag",
    "ontology_text_rag",
)
METHOD_SHORT = {
    "prompt_only": "Prompt only",
    "prompt_rag": "Text RAG",
    "ontology_prompt_rag": "Structured ontology",
    "ontology_text_rag": "Ontology to text",
}
MODEL_LABELS = {
    "mistral_7b": "Mistral 7B",
    "qwen2_5_7b": "Qwen2.5 7B",
    "qwen3_8b": "Qwen3 8B",
}

BIB_ENTRIES = r"""

@article{greco2019composite,
  author  = {Greco, Salvatore and Ishizaka, Alessio and Tasiou, Menelaos and Torrisi, Gianpiero},
  title   = {On the Methodological Framework of Composite Indices: A Review of the Issues of Weighting, Aggregation, and Robustness},
  journal = {Social Indicators Research},
  volume  = {141},
  pages   = {61--94},
  year    = {2019},
  doi     = {10.1007/s11205-017-1832-9}
}

@article{becker2017weights,
  author  = {Becker, William and Saisana, Michaela and Paruolo, Paolo and Vandecasteele, Ine},
  title   = {Weights and Importance in Composite Indicators: Closing the Gap},
  journal = {Ecological Indicators},
  volume  = {80},
  pages   = {12--22},
  year    = {2017},
  doi     = {10.1016/j.ecolind.2017.03.056}
}
""".strip()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _extract_between(text: str, start: str, end: str, *, include_end: bool = False) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    if include_end:
        end_index += len(end)
    return text[start_index:end_index]


def _replace_between(text: str, start: str, end: str, replacement: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[:start_index] + replacement + text[end_index:]


def _replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected exactly one {label} block; found {count}.")
    return text.replace(old, new, 1)


def _protected_blocks(text: str) -> Dict[str, str]:
    return {
        "title": re.search(r"\\title\{[^\n\r]+\}", text).group(0),
        "running_title": re.search(r"\\titlerunning\{[^\n\r]+\}", text).group(0),
        "author_metadata": _extract_between(text, r"\author{", r"\maketitle", include_end=True),
        "abstract_environment": _extract_between(
            text, r"\begin{abstract}", r"\end{abstract}", include_end=True
        ),
        "keywords": re.search(
            r"\\keywords\{.*?\}", text, flags=re.DOTALL
        ).group(0),
        "introduction": _extract_between(
            text, r"\section{Introduction}", r"\section{Related Work}"
        ),
        "four_generation_modes": _extract_between(
            text,
            r"\subsection{Four Generation Modes}",
            r"\subsection{Worked Scenario Example}",
        ),
        "layer_1_results": _extract_between(
            text,
            r"\subsection{Layer 1 Results: Ontology Functional Validation}",
            r"\subsection{Layer 2 Results: Common Scenario Conformance}",
        ),
        "layer_2_results": _extract_between(
            text,
            r"\subsection{Layer 2 Results: Common Scenario Conformance}",
            r"\subsection{Layer 3 Results: Method and Model Comparison}",
        ),
        "diversity_definition": _extract_between(
            text,
            r"\paragraph{Diversity.}",
            r"\subsection{Layer 3: Method and Model Comparison}",
        ),
        "diversity_results": _extract_between(
            text,
            r"\paragraph{Diversity and repetition.}",
            "No output contained invalid JSON",
        ),
    }


def _method_table(method_rows: Sequence[Mapping[str, str]]) -> str:
    by_method = {row["method"]: row for row in method_rows}
    metric_specs = [
        ("json_validity_J_up", "max"),
        ("control_adherence_A_up", "max"),
        ("required_concept_precision_P_up", "max"),
        ("required_concept_recall_R_up", "max"),
        ("required_concept_f1_F1req_up", "max"),
        ("provenance_field_completeness_G_up", "max"),
        ("traceability_T_up", "max"),
        ("ontology_scope_up", "max"),
        ("contradiction_rate_E_down", "min"),
        ("oci_equal_weight_secondary", "max"),
    ]
    values_by_metric: Dict[str, List[float]] = {}
    for metric, _direction in metric_specs:
        values_by_metric[metric] = [
            float(by_method[method][metric])
            for method in METHOD_ORDER
            if by_method[method][metric] != ""
        ]

    table_rows: List[str] = []
    for method in METHOD_ORDER:
        row = by_method[method]
        cells: List[str] = []
        for metric, direction in metric_specs:
            raw_value = row[metric]
            if raw_value == "":
                cells.append("--")
                continue
            value = float(raw_value)
            target = (
                max(values_by_metric[metric])
                if direction == "max"
                else min(values_by_metric[metric])
            )
            formatted = f"{value:.3f}".lstrip("0")
            if abs(value - target) <= 5e-7:
                formatted = rf"\textbf{{{formatted}}}"
            cells.append(formatted)
        table_rows.append(
            f"{METHOD_SHORT[method]:<22} & " + " & ".join(cells) + r"\\"
        )

    return "\n".join(
        [
            r"\begin{table}[!h]",
            r"\caption{Mean method diagnostics across three models ($n=360$ per condition).}",
            r"\label{tab:method}",
            r"\centering",
            r"\fontsize{6.25}{6.9}\selectfont",
            r"\setlength{\tabcolsep}{1.05pt}",
            r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{1.72cm}rrrrrrrrrr@{}}",
            r"\toprule",
            r"\textbf{Condition} & \textbf{$J\uparrow$} & \textbf{$A\uparrow$} &",
            r"\textbf{$P\uparrow$} & \textbf{$R\uparrow$} & \textbf{$F1_{\rm req}\uparrow$} &",
            r"\textbf{$G\uparrow$} & \textbf{$T\uparrow$} &",
            r"\shortstack{\textbf{Ont.}\\\textbf{scope}$\uparrow$} &",
            r"\textbf{$E\downarrow$} & \textbf{OCI$_{\rm eq}\uparrow$}\\",
            r"\midrule",
            *table_rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{2pt}",
            r"\begin{minipage}{0.97\textwidth}",
            r"\fontsize{7.0}{7.6}\selectfont",
            (
                r"\emph{Symbols:} $J$, JSON validity; $A$, control adherence; $P$ and $R$, "
                r"method-conditioned required-concept precision and recall; "
                r"$F1_{\rm req}$, their harmonic mean; $G$, required provenance-field "
                r"presence; $T$, resolution of declared links to frozen local records; "
                r"Ont. scope, ontology trace/control coverage; $E$, contradiction rate. "
                r"$T$ is conditional on declared links (applicable $n$: 0, 226, 360, and "
                r"360); ``--'' means not applicable. Component metrics are primary; "
                r"OCI$_{\rm eq}$ is the secondary descriptive summary in "
                r"Eq.~\ref{eq:operational-index}."
            ),
            r"\end{minipage}",
            r"\end{table}",
        ]
    )


def _model_table(model_rows: Sequence[Mapping[str, str]]) -> str:
    lookup = {
        (row["model_key"], row["method"]): float(row["oci_equal_weight_secondary"])
        for row in model_rows
    }
    table_rows: List[str] = []
    for model_key in ("mistral_7b", "qwen2_5_7b", "qwen3_8b"):
        values = [lookup[(model_key, method)] for method in METHOD_ORDER]
        maximum = max(values)
        cells = []
        for value in values:
            formatted = f"{value:.4f}".lstrip("0")
            if abs(value - maximum) <= 5e-7:
                formatted = rf"\textbf{{{formatted}}}"
            cells.append(formatted)
        table_rows.append(
            f"{MODEL_LABELS[model_key]} & " + " & ".join(cells) + r"\\"
        )
    means = [
        sum(lookup[(model, method)] for model in MODEL_LABELS) / len(MODEL_LABELS)
        for method in METHOD_ORDER
    ]
    maximum_mean = max(means)
    mean_cells = []
    for value in means:
        formatted = f"{value:.4f}".lstrip("0")
        if abs(value - maximum_mean) <= 5e-7:
            formatted = rf"\textbf{{{formatted}}}"
        mean_cells.append(formatted)
    return "\n".join(
        [
            r"\begin{table}[!h]",
            r"\caption{Secondary OCI$_{\rm eq}$ by model and condition.}",
            r"\label{tab:model-index}",
            r"\centering",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{5.0pt}",
            r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.65cm}rrrr@{}}",
            r"\toprule",
            r"\textbf{Model} & \textbf{A: Prompt} & \textbf{B: Text RAG} &",
            r"\textbf{C: Structured} & \textbf{D: Ontology text}\\",
            r"\midrule",
            *table_rows,
            r"\midrule",
            "Mean       & " + " & ".join(mean_cells) + r"\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )


def _five_case_table(cases: Sequence[Mapping[str, Any]]) -> str:
    row_by_type = {case["selection_type"]: case for case in cases}
    ordered_types = (
        "representative_median_performing",
        "ontology_to_text_contradiction",
        "external_rag_returned_no_text",
        "legitimate_communication",
        "clearest_precision_recall_tradeoff",
    )
    labels = {
        "representative_median_performing": "Median pair",
        "ontology_to_text_contradiction": "Contradiction",
        "external_rag_returned_no_text": "No ext. RAG",
        "legitimate_communication": "Legitimate",
        "clearest_precision_recall_tradeoff": "P/R trade-off",
    }
    observations: Dict[str, str] = {}
    for selection_type in ordered_types:
        case = row_by_type[selection_type]
        comparisons = {row["method"]: row for row in case["comparisons"]}
        if selection_type == "representative_median_performing":
            observations[selection_type] = (
                "All modes pass $E$ and safe action; pair OCI$_{\\rm eq}$ is nearest "
                "the complete-pair median."
            )
        elif selection_type == "ontology_to_text_contradiction":
            c4 = comparisons["ontology_text_rag"]
            observations[selection_type] = (
                f"Mode D has $E={c4['contradiction_E']}$ and requires regeneration; "
                "matched A--C have $E=0$."
            )
        elif selection_type == "external_rag_returned_no_text":
            observations[selection_type] = (
                "Mode B retrieved no context, so $T$ is not applicable; its shared gate passed."
            )
        elif selection_type == "legitimate_communication":
            observations[selection_type] = (
                "All modes retain the legitimate label and safe workflow without contradiction."
            )
        else:
            c4 = comparisons["ontology_text_rag"]
            observations[selection_type] = (
                f"Mode D exposes $P={c4['required_concept_precision']:.3f}$ and "
                f"$R={c4['required_concept_recall']:.3f}$, the largest disclosed gap."
            )
    rows = []
    for selection_type in ordered_types:
        case = row_by_type[selection_type]
        pair = (
            f"{case['case_id'].replace('PSQ-SCO-120-', '')}/"
            f"{MODEL_LABELS[case['model_key']]}"
        )
        rows.append(
            f"{labels[selection_type]} & {pair} & {observations[selection_type]}\\\\"
        )
    return "\n".join(
        [
            r"\subsubsection{Five matched diagnostic cases.}",
            (
                r"Table~\ref{tab:five-cases} compares all four stored outputs for each "
                r"deterministically selected case/model pair. The supplement gives verbatim "
                r"excerpts, concept lists, $G$, $T$, $E$, and safe-action results."
            ),
            "",
            r"\begin{table}[!h]",
            r"\caption{Deterministically selected matched-case diagnostics.}",
            r"\label{tab:five-cases}",
            r"\centering",
            r"\fontsize{7.0}{7.6}\selectfont",
            r"\setlength{\tabcolsep}{2.5pt}",
            r"\begin{tabularx}{0.97\textwidth}{@{}>{\raggedright\arraybackslash}p{1.7cm}>{\raggedright\arraybackslash}p{2.15cm}X@{}}",
            r"\toprule",
            r"\textbf{Selection} & \textbf{Case/model} & \textbf{Matched observation}\\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{table}",
        ]
    )


def _layer_three_replacement(
    method_rows: Sequence[Mapping[str, str]],
    model_rows: Sequence[Mapping[str, str]],
    sensitivity: Mapping[str, Any],
    cases: Sequence[Mapping[str, Any]],
) -> str:
    overall = sensitivity["scopes"]["overall"]
    first = overall["first_place_proportions"]
    pair_stability = overall["pairwise_rank_stability"]
    prompt_text_stability = pair_stability["prompt_only_vs_prompt_rag"]["stability"]
    prompt_c4_stability = pair_stability[
        "prompt_only_vs_ontology_text_rag"
    ]["stability"]
    text_c4_stability = pair_stability[
        "prompt_rag_vs_ontology_text_rag"
    ]["stability"]
    return "\n\n".join(
        [
            _method_table(method_rows),
            (
                "Structured ontology has the highest method-conditioned $P$ (.508) and "
                "$F1_{\\rm req}$ (.545); ontology to text has the highest $R$ (.809). "
                "$G$ is complete for C and D. Conditional mean $T$ is .996 for C, .968 "
                "for D, and .928 for B; A declares no links. $E$ is zero for A--C and "
                ".003 for D. "
                "External text was returned for 226 Text-RAG, 221 structured-ontology, and "
                "242 ontology-to-text rows; every ontology row retains identifiers."
            ),
            (
                "OCI$_{\\rm eq}$ orders the tested conditions C, D, B, A with means .909, "
                ".879, .846, and .799. Legacy weights give the same condition and "
                "within-model ranks."
            ),
            (
                "Table~\\ref{tab:model-index} is a secondary stability view: C is highest "
                "for each model, conditional on these components rather than universal quality."
            ),
            _model_table(model_rows),
            (
                f"In 10,000 deterministic weight samples, C ranks first in "
                f"{100 * first['ontology_prompt_rag']:.1f}\\%; pairwise stability is "
                f"{100 * prompt_text_stability:.1f}\\% for B versus A, "
                f"{100 * prompt_c4_stability:.1f}\\% for D versus A, and "
                f"{100 * text_c4_stability:.1f}\\% for D versus B. "
                "Components therefore remain primary."
            ),
            _five_case_table(cases),
            "",
        ]
    )


def update_manuscript(
    source_text: str,
    *,
    method_rows: Sequence[Mapping[str, str]],
    model_rows: Sequence[Mapping[str, str]],
    sensitivity: Mapping[str, Any],
    cases: Sequence[Mapping[str, Any]],
) -> Tuple[str, List[str]]:
    newline = "\r\n" if "\r\n" in source_text else "\n"

    def nl(value: str) -> str:
        return value.replace("\n", newline)

    changes: List[str] = []
    text = source_text

    old_figure = r"\includegraphics[width=1.10\textwidth]{PSQ_SCO_Compact_Framework_Fig1_Updated.png}"
    new_figure = r"\includegraphics[width=\textwidth]{PSQ_SCO_Compact_Framework_Fig1_Updated.png}"
    text = _replace_exact(text, old_figure, new_figure, "Figure 1 width")
    changes.append("Figure 1 width constrained from 1.10\\textwidth to \\textwidth.")

    evidence_replacement = nl(
        r"""\paragraph{Evidence grounding.}
$G$ is the fraction of six required source/provenance fields present. For output
$c$, $L_c$ contains its declared source, dataset, provenance-record, and ordered
context links; $V_c\subseteq L_c$ contains those resolving to the correct frozen
local record. Thus $T_c=|V_c|/|L_c|$, or not applicable if $L_c$ is empty.
Neither $G$ nor $T$ proves claim--source support, which remains unevaluated;
retrieval relevance and generation faithfulness are distinct \cite{es2024ragas}."""
    ) + newline * 2
    text = _replace_between(
        text,
        r"\paragraph{Evidence grounding.}",
        r"\paragraph{Secondary mechanism diagnostics.}",
        evidence_replacement,
    )
    changes.append("Separated provenance-field completeness G from canonical traceability T.")

    mechanism_replacement = nl(
        r"""\paragraph{Secondary mechanism diagnostics.}
The method-conditioned required-concept scores may include packet terms and
provenance available only to a given mode. They explain mechanism exposure rather
than cross-mode accuracy. A separate ontology-scope diagnostic counts implemented
channel, attack, cue, response, evidence, and non-contradiction checks in the
trace; it is a rule audit, not OWL entailment or ontology-embedding accuracy.

Composite indices can summarize multidimensional diagnostics, but their
interpretation depends on weighting and aggregation; nominal weights may not
equal empirical influence, so components and weight sensitivity should be reported
\cite{greco2019composite,becker2017weights}. Accordingly, we treat the component
metrics as primary and report the equal-weight operational index only as a
secondary descriptive summary:
\begin{equation}
\mathrm{OCI}_{\mathrm{eq}}=
\frac{J+A+F_{\mathrm{req}}+G+(1-E)}{5},
\label{eq:operational-index}
\end{equation}
where $J$, $A$, $F_{\mathrm{req}}$, $G$, and $E$ denote JSON validity, control
adherence, method-conditioned concept F1, provenance completeness, and
contradiction rate. Equal nominal weights express the absence of a validated
differential model, not objective fairness. OCI$_{\mathrm{eq}}$ is secondary,
descriptive, uncalibrated, and neither a quality percentage, threshold, nor
learner-effect measure. Sensitivity compares the earlier engine-priority weights."""
    ) + newline * 2
    text = _replace_between(
        text,
        r"\paragraph{Secondary mechanism diagnostics.}",
        r"\paragraph{Contradiction and technical decision.}",
        mechanism_replacement,
    )
    changes.append("Replaced the principal unequal OCI with equal-weight secondary OCI_eq.")

    old_stats = (
        "Schema,\ncontrol, and common-case concept scores are validation results. "
        "The operational\ncontrol index in Eq.~\\ref{eq:operational-index} and the "
        "diversity measures describe differences\nbetween implemented representations; "
        "they are not general quality rankings."
    )
    new_stats = (
        "Schema,\ncontrol, and common-case concept scores are validation results. "
        "The secondary\nequal-weight operational index in "
        "Eq.~\\ref{eq:operational-index} and the diversity measures describe "
        "differences\nbetween implemented representations; they are not general "
        "quality rankings."
    )
    text = _replace_exact(text, nl(old_stats), nl(new_stats), "statistical OCI sentence")
    changes.append("Clarified the secondary status of OCI_eq in statistical analysis.")

    layer_three = nl(
        _layer_three_replacement(method_rows, model_rows, sensitivity, cases)
    )
    text = _replace_between(
        text,
        nl(
            r"""\begin{table}[!h]
\caption{Method diagnostics and OCI ($n=360$ per condition).}"""
        ),
        r"\paragraph{Diversity and repetition.}",
        layer_three,
    )
    changes.append("Regenerated method/model tables and inserted five matched cases.")

    old_discussion = (
        "Structured\nontology leads OCI and three diversity measures, whereas ontology "
        "to text has the\nlowest title repetition."
    )
    new_discussion = (
        "Structured\nontology has the highest method-conditioned precision, F1, and "
        "traceability and leads three diversity measures; ontology to text has the\n"
        "lowest title repetition."
    )
    text = _replace_exact(
        text, nl(old_discussion), nl(new_discussion), "discussion component sentence"
    )
    old_auditability = (
        "Rather, structured guidance provides\ngreater provenance, typed control "
        "exposure, and auditability under the tested OCI."
    )
    new_auditability = (
        "Rather, structured guidance provides\ngreater provenance, typed control "
        "exposure, and auditability. Its first-place OCI$_{\\rm eq}$ rank is descriptive, "
        "not universal."
    )
    text = _replace_exact(
        text, nl(old_auditability), nl(new_auditability), "discussion auditability sentence"
    )
    changes.append("Made Discussion component-first and bounded the OCI_eq claim.")

    old_threat = (
        "Source similarity lacks frozen relevance\njudgments, diversity uses one "
        "embedding model, and English email, SMS, and voice\ncases do not cover every "
        "culture, organization, or attack family."
    )
    new_threat = (
        "Link resolution verifies paths, not claim support; source similarity lacks "
        "frozen relevance\njudgments. OCI$_{\\rm eq}$ is uncalibrated, although nominal "
        "ranks and 10,000-weight sensitivity are reported. Diversity uses "
        "one embedding model, and English email, SMS, and voice\ncases do not cover "
        "every culture, organization, or attack family."
    )
    text = _replace_exact(text, nl(old_threat), nl(new_threat), "validity paragraph")
    changes.append("Added traceability and composite-index threats to validity.")

    old_limit = (
        "Evidence fields support auditing but do not\nprove source quality; experts "
        "must review accepted scenarios and mappings."
    )
    new_limit = (
        "Evidence fields and local paths support auditing but do not\nprove source "
        "quality or claim support; experts must review scenarios and mappings. One "
        "run and schema-safe repairs limit decoding and content-stability inference."
    )
    text = _replace_exact(text, nl(old_limit), nl(new_limit), "limitations evidence sentence")
    changes.append("Distinguished resolvable paths from evidence support in Limitations.")

    old_conclusion = (
        "OCI was .774 for prompt only, .818\nfor Text RAG, .849 for ontology to text, "
        "and .886 for structured ontology, which\nranked highest for every tested model. "
        "Because common conformance reached ceiling\nperformance "
        "(Section~\\ref{subsection:diag}), this result indicates stronger\ntraceability "
        "and mechanism exposure in the tested setting, not superior scenario\nquality "
        "in general."
    )
    new_conclusion = (
        "Structured ontology has the highest method-conditioned precision, F1, and "
        "mean traceability; ontology to text has the highest recall. Secondary "
        "OCI$_{\\rm eq}$ is .799, .846, .909, and .879 for A--D, with C highest for "
        "each model under both nominal weightings. Because common conformance reached "
        "ceiling performance (Section~\\ref{subsection:diag}), these results indicate "
        "mechanism exposure, not superior scenario quality in general."
    )
    text = _replace_exact(text, nl(old_conclusion), nl(new_conclusion), "conclusion OCI block")
    changes.append("Updated only OCI/traceability-dependent conclusion sentences.")
    return text, changes


def _citation_check(tex: str, bib: str) -> Dict[str, Any]:
    cited: set[str] = set()
    for match in re.finditer(r"\\cite\{([^}]+)\}", tex):
        cited.update(part.strip() for part in match.group(1).split(","))
    bib_keys = set(re.findall(r"@\w+\{\s*([^,\s]+)", bib))
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", tex))
    return {
        "cited_keys": sorted(cited),
        "bibliography_keys": sorted(bib_keys),
        "missing_citations": sorted(cited - bib_keys),
        "missing_references": sorted(refs - labels),
    }


def create_package(
    *,
    manuscript_source: Path,
    package_source: Path,
    evaluation_dir: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True)

    source_bytes = manuscript_source.read_bytes()
    source_text = source_bytes.decode("utf-8")
    protected_before = _protected_blocks(source_text)
    method_rows = _read_csv(evaluation_dir / "method_summary.csv")
    model_rows = _read_csv(evaluation_dir / "model_summary.csv")
    sensitivity = json.loads(
        (evaluation_dir / "weight_sensitivity_summary.json").read_text(encoding="utf-8")
    )
    cases = json.loads(
        (evaluation_dir / "five_matched_cases.json").read_text(encoding="utf-8")
    )

    revised_text, changes = update_manuscript(
        source_text,
        method_rows=method_rows,
        model_rows=model_rows,
        sensitivity=sensitivity,
        cases=cases,
    )
    protected_after = _protected_blocks(revised_text)
    protected_comparison = {
        key: {
            "before_sha256": _sha256_bytes(value.encode("utf-8")),
            "after_sha256": _sha256_bytes(protected_after[key].encode("utf-8")),
            "byte_identical": value.encode("utf-8") == protected_after[key].encode("utf-8"),
            "byte_length": len(value.encode("utf-8")),
        }
        for key, value in protected_before.items()
    }
    changed_protected = [
        key for key, result in protected_comparison.items() if not result["byte_identical"]
    ]
    if changed_protected:
        raise RuntimeError(f"Protected manuscript blocks changed: {changed_protected}")

    (output_dir / "main_original.tex").write_bytes(source_bytes)
    (output_dir / "main.tex").write_text(revised_text, encoding="utf-8", newline="")

    bib_source = package_source / "references.bib"
    bib_text = bib_source.read_text(encoding="utf-8")
    (output_dir / "references_original.bib").write_text(
        bib_text, encoding="utf-8", newline=""
    )
    if "10.1007/s11205-017-1832-9" not in bib_text:
        bib_text = bib_text.rstrip() + "\n\n" + BIB_ENTRIES + "\n"
    elif "10.1016/j.ecolind.2017.03.056" not in bib_text:
        raise RuntimeError("Only one DOI-matched composite-index reference already exists.")
    (output_dir / "references.bib").write_text(bib_text, encoding="utf-8", newline="")

    for filename in (
        "llncs.cls",
        "splncs04.bst",
        "PSQ_SCO_Compact_Framework_Fig1_Updated.png",
    ):
        shutil.copy2(package_source / filename, output_dir / filename)

    citation_check = _citation_check(revised_text, bib_text)
    if citation_check["missing_citations"] or citation_check["missing_references"]:
        raise RuntimeError(f"Static citation/reference check failed: {citation_check}")

    forbidden = {
        token: [match.start() for match in re.finditer(re.escape(token), revised_text)]
        for token in ("OCI=", ".20J", ".25A", ".25F", "No contr.", "F1_EQ", "REQ")
    }
    forbidden = {key: value for key, value in forbidden.items() if value}
    if forbidden:
        raise RuntimeError(f"Forbidden principal-paper strings remain: {forbidden}")

    snapshot = {
        "source_path": str(manuscript_source.resolve()),
        "source_sha256": _sha256_bytes(source_bytes),
        "protected_blocks": {
            key: {
                "text": value,
                **protected_comparison[key],
            }
            for key, value in protected_before.items()
        },
    }
    (output_dir / "protected_blocks_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "TARGETED_CHANGES.md").write_text(
        "# Targeted LaTeX Changes\n\n"
        + "\n".join(f"- {change}" for change in changes)
        + "\n\nNo other manuscript blocks were intentionally changed.\n",
        encoding="utf-8",
    )

    files = [
        path
        for path in output_dir.iterdir()
        if path.is_file() and path.name != "latex_update_manifest.json"
    ]
    manifest = {
        "source_manuscript": str(manuscript_source.resolve()),
        "source_sha256": _sha256_bytes(source_bytes),
        "revised_main_sha256": _sha256_bytes(revised_text.encode("utf-8")),
        "evaluation_dir": str(evaluation_dir.resolve()),
        "protected_blocks_all_byte_identical": True,
        "protected_block_comparison": protected_comparison,
        "changes": changes,
        "citation_check": citation_check,
        "forbidden_string_check": {
            "tokens": ["OCI=", ".20J", ".25A", ".25F", "No contr.", "F1_EQ", "REQ"],
            "matches": forbidden,
            "passed": not forbidden,
        },
        "figure_width_check": {
            "contains_1_10_textwidth": r"1.10\textwidth" in revised_text,
            "contains_textwidth": (
                r"\includegraphics[width=\textwidth]" in revised_text
            ),
        },
        "file_sha256": {path.name: _sha256_file(path) for path in sorted(files)},
    }
    (output_dir / "latex_update_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create the non-overwriting targeted PSQ-SCO Overleaf revision."
    )
    parser.add_argument("--manuscript-source", type=Path, default=DEFAULT_MANUSCRIPT_SOURCE)
    parser.add_argument("--package-source", type=Path, default=DEFAULT_PACKAGE_SOURCE)
    parser.add_argument("--evaluation-dir", type=Path, default=DEFAULT_EVALUATION_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = create_package(
        manuscript_source=args.manuscript_source,
        package_source=args.package_source,
        evaluation_dir=args.evaluation_dir,
        output_dir=args.out_dir,
    )
    print(
        json.dumps(
            {
                "output_dir": str(args.out_dir.resolve()),
                "protected_blocks_all_byte_identical": manifest[
                    "protected_blocks_all_byte_identical"
                ],
                "missing_citations": manifest["citation_check"]["missing_citations"],
                "missing_references": manifest["citation_check"]["missing_references"],
                "figure_width_check": manifest["figure_width_check"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
