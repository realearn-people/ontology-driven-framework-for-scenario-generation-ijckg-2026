from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
from pathlib import Path

try:
    from rdflib import Graph
except ImportError:
    print(
        "RDFLib is required. Install the checkout's minimal requirements, then re-run:\n"
        "  python ontology/scripts/run_sparql_cq_v9_1.py --cq all",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ONTOLOGY = ROOT / "ontology" / "personashield-psq-sco-v9.1.owl"
QUERY_ROOT = ROOT / "queries" / "v9_1"
VALIDATION_ROOT = QUERY_ROOT / "validation"
OUTPUT_ROOT = ROOT / "outputs" / "v9_1"
BASE = "http://personashield.ait.ac.th/ontology/psq-sco#"

CQ_FILES = {
    "1": QUERY_ROOT / "cq1-select-templates.rq",
    "2": QUERY_ROOT / "cq2-cybersecurity-structure.rq",
    "3": QUERY_ROOT / "cq3-content-quality-control.rq",
    "4": QUERY_ROOT / "cq4-evidence-provenance.rq",
}

CQ_NAMES = {
    "1": "Scenario Selection",
    "2": "Cybersecurity Structure",
    "3": "Content Quality Control",
    "4": "Evidence and Provenance Grounding",
}

LOCAL_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def validate_local_id(value: str, label: str) -> str:
    if not LOCAL_ID.fullmatch(value):
        raise SystemExit(f"Invalid {label}: {value!r}")
    return value


def bind_values(query: str, learner: str, template: str) -> str:
    query = re.sub(
        r"VALUES\s+\?learner\s*\{\s*psq:[^}\s]+\s*\}",
        f"VALUES ?learner {{ psq:{learner} }}",
        query,
        count=1,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"VALUES\s+\?template\s*\{\s*psq:[^}\s]+\s*\}",
        f"VALUES ?template {{ psq:{template} }}",
        query,
        count=1,
        flags=re.IGNORECASE,
    )
    return query


def compact(value):
    if value is None:
        return None
    text = str(value)
    if text.startswith(BASE):
        return f"psq:{text[len(BASE):]}"
    return text


def execute_query(graph: Graph, text: str):
    started = time.perf_counter()
    result = graph.query(text)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    if result.type == "ASK":
        return {"type": "ASK", "boolean": bool(result.askAnswer)}, elapsed_ms
    variables = [str(v) for v in result.vars]
    rows = []
    for row in result:
        rows.append({variable: compact(row[index]) for index, variable in enumerate(variables)})
    return {"type": str(result.type), "variables": variables, "row_count": len(rows), "rows": rows}, elapsed_ms


def load_graph(path: Path):
    started = time.perf_counter()
    graph = Graph()
    graph.parse(path, format="xml")
    return graph, round((time.perf_counter() - started) * 1000, 3)


def run_cq(graph: Graph, cq: str, learner: str, scenario_template: str, evidence_template: str):
    template = evidence_template if cq == "4" else scenario_template
    query = bind_values(CQ_FILES[cq].read_text(encoding="utf-8"), learner, template)
    result, elapsed_ms = execute_query(graph, query)
    return {
        "cq": f"CQ{cq}",
        "name": CQ_NAMES[cq],
        "query_file": str(CQ_FILES[cq].relative_to(ROOT)).replace("\\", "/"),
        "parameters": {
            "learner": learner if cq in {"1"} else None,
            "template": template if cq in {"2", "3", "4"} else None,
        },
        "execution_ms": elapsed_ms,
        "result": result,
    }


def run_validation_cases(graph: Graph):
    cases = []
    for path in sorted(VALIDATION_ROOT.glob("*.ask.rq")):
        result, elapsed_ms = execute_query(graph, path.read_text(encoding="utf-8"))
        actual = result.get("boolean")
        cases.append(
            {
                "test_id": path.name.removesuffix(".ask.rq"),
                "query_file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "expected": True,
                "actual": actual,
                "passed": result["type"] == "ASK" and actual is True,
                "execution_ms": elapsed_ms,
            }
        )
    return {
        "ontology_version": "9.1.0",
        "validation_type": "SPARQL ASK competency-question cases",
        "case_count": len(cases),
        "passed_count": sum(c["passed"] for c in cases),
        "failed_count": sum(not c["passed"] for c in cases),
        "status": "PASS" if cases and all(c["passed"] for c in cases) else "FAIL",
        "cases": cases,
    }


def table_text(payload: dict) -> str:
    if payload["type"] == "ASK":
        return f"ASK result: {str(payload['boolean']).lower()}"
    variables = payload["variables"]
    rows = payload["rows"]
    if not rows:
        return "(no rows)"
    widths = {
        var: min(50, max(len(var), *(len(str(row.get(var) or "")) for row in rows)))
        for var in variables
    }
    def render(row):
        cells = []
        for var in variables:
            value = str(row.get(var) or "")
            if len(value) > widths[var]:
                value = value[: widths[var] - 1] + "..."
            cells.append(value.ljust(widths[var]))
        return " | ".join(cells)
    return "\n".join(
        [
            render({var: var for var in variables}),
            "-+-".join("-" * widths[var] for var in variables),
            *(render(row) for row in rows),
        ]
    )


def csv_text(payload: dict) -> str:
    if payload["type"] == "ASK":
        return "boolean\n" + str(payload["boolean"]).lower() + "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=payload["variables"])
    writer.writeheader()
    writer.writerows(payload["rows"])
    return output.getvalue()


def emit(payload: dict, fmt: str):
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif fmt == "csv":
        if "type" in payload:
            print(csv_text(payload), end="")
        else:
            output = io.StringIO(newline="")
            rows = payload.get("cases", [])
            fields = ["test_id", "expected", "actual", "passed", "execution_ms", "query_file"]
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows({field: row.get(field) for field in fields} for row in rows)
            print(output.getvalue(), end="")
    else:
        if "type" in payload:
            print(table_text(payload))
        else:
            print(
                f"Status: {payload.get('status', 'UNKNOWN')} | "
                f"Passed: {payload.get('passed_count', 0)}/{payload.get('case_count', 0)}"
            )
            for case in payload.get("cases", []):
                marker = "PASS" if case.get("passed") else "FAIL"
                print(f"{marker}: {case.get('test_id')} ({case.get('execution_ms')} ms)")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PSQ-SCO v9.1 SPARQL CQ queries.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--cq", choices=["1", "2", "3", "4", "all"])
    action.add_argument("--validate-cases", action="store_true")
    action.add_argument("--full", action="store_true")
    action.add_argument("--list-queries", action="store_true")
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument("--learner", default="Learner_HR_Beginner")
    parser.add_argument("--scenario-template", default="TPL_SMS_BankLink_Introductory")
    parser.add_argument("--evidence-template", default="TPL_Voice_ITSupport_Advanced")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.list_queries:
        for key, path in CQ_FILES.items():
            print(f"CQ{key}: {CQ_NAMES[key]} -> {path.relative_to(ROOT)}")
        print(f"Validation ASK queries: {VALIDATION_ROOT.relative_to(ROOT)}")
        return 0

    validate_local_id(args.learner, "learner")
    validate_local_id(args.scenario_template, "scenario-template")
    validate_local_id(args.evidence_template, "evidence-template")

    ontology = args.ontology if args.ontology.is_absolute() else ROOT / args.ontology
    graph, load_ms = load_graph(ontology)

    if args.validate_cases:
        payload = run_validation_cases(graph)
        emit(payload, args.format)
        if args.output:
            write_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
        else:
            write_json(OUTPUT_ROOT / "sparql-cq-validation-report.json", payload)
        return 0 if payload["status"] == "PASS" else 1

    cqs = ["1", "2", "3", "4"] if args.cq == "all" or args.full else [args.cq]
    results = [
        run_cq(graph, cq, args.learner, args.scenario_template, args.evidence_template)
        for cq in cqs
    ]
    payload = {
        "ontology": str(ontology),
        "ontology_version": "9.1.0",
        "triple_count": len(graph),
        "load_ms": load_ms,
        "cq_results": results,
    }
    if args.full:
        payload["validation_cases"] = run_validation_cases(graph)
    if args.output:
        write_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    elif args.cq == "all" or args.full:
        write_json(OUTPUT_ROOT / "sparql-cq-full-run-report.json", payload)

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif len(results) == 1:
        emit(results[0]["result"], args.format)
    else:
        for result in results:
            print(f"\n{result['cq']} - {result['name']}")
            print(table_text(result["result"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
