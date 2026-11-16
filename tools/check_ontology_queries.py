#!/usr/bin/env python3
"""Re-run the four default competency queries and the eight ASK fixtures."""

from pathlib import Path
from rdflib import Graph

from ontology_reference import ROOT, ontology_path


def main() -> int:
    path = ontology_path()
    query_root = path.parent.parent / "queries" / "v9_1"
    answers = {
        "cq1-select-templates.rq": 2,
        "cq2-cybersecurity-structure.rq": 13,
        "cq3-content-quality-control.rq": 8,
        "cq4-evidence-provenance.rq": 12,
    }
    graph = Graph().parse(path, format="xml")
    for filename, expected in answers.items():
        result = graph.query((query_root / filename).read_text(encoding="utf-8"))
        actual = len(list(result))
        if result.type != "SELECT" or actual != expected:
            raise ValueError(f"{filename}: expected {expected} SELECT rows, got {actual}")
        print(f"PASS: {filename}: {actual} rows")

    expected_names = {
        f"CQ{query}-{case}-001.ask.rq"
        for query in range(1, 5) for case in ("POS", "NEG")
    }
    fixtures = sorted((query_root / "validation").glob("*.ask.rq"))
    if {file.name for file in fixtures} != expected_names:
        raise ValueError("Expected one positive and one negative ASK fixture for each CQ")
    for file in fixtures:
        result = graph.query(file.read_text(encoding="utf-8"))
        # Negative fixtures express the rejection condition, so their assertion
        # must also evaluate true.
        if result.type != "ASK" or result.askAnswer is not True:
            raise ValueError(f"{file.relative_to(ROOT).as_posix()}: ASK assertion failed")
    print("PASS: 8/8 positive/negative ASK assertions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
