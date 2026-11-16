#!/usr/bin/env python3
"""Build or verify an English reference for every term declared in PSQ-SCO v9.1."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ONTOLOGY_REFERENCE.md"
OWL_FILE = "personashield-psq-sco-v9.1.owl"
NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "psq": "http://personashield.ait.ac.th/ontology/psq-sco#",
    "prov": "http://www.w3.org/ns/prov#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
ABOUT = "{" + NS["rdf"] + "}about"
RESOURCE = "{" + NS["rdf"] + "}resource"


def ontology_path() -> Path:
    paths = (ROOT / "ontology" / OWL_FILE, ROOT / "ontology" / "ontology" / OWL_FILE)
    existing = [path for path in paths if path.is_file()]
    if len(existing) != 1:
        raise ValueError("Expected one bundled PSQ-SCO v9.1 OWL file")
    return existing[0]


def term(uri: str) -> str:
    for prefix, namespace in NS.items():
        if uri.startswith(namespace):
            return f"{prefix}:{uri[len(namespace):]}"
    return uri


def cell(value: str) -> str:
    return " ".join(value.split()).replace("|", r"\|") or "—"


def types(nodes: list[ET.Element]) -> set[str]:
    result = set()
    for node in nodes:
        if node.tag.startswith("{" + NS["owl"] + "}"):
            result.add("owl:" + node.tag.split("}", 1)[1])
        result.update(term(child.attrib[RESOURCE]) for child in node.findall("rdf:type", NS)
                      if RESOURCE in child.attrib)
    return result


def literal(nodes: list[ET.Element], *names: str) -> str:
    for name in names:
        values = [n for node in nodes for n in node.findall(name, NS) if (n.text or "").strip()]
        values.sort(key=lambda n: (n.get(XML_LANG, "") != "en", n.get(XML_LANG, "") != ""))
        if values:
            return values[0].text or ""
    return ""


def links(nodes: list[ET.Element], name: str) -> str:
    values = sorted({term(n.attrib[RESOURCE]) for node in nodes for n in node.findall(name, NS)
                     if RESOURCE in n.attrib})
    return ", ".join(f"\x60{value}\x60" for value in values) or "—"


def table(lines: list[str], headers: tuple[str, ...], rows) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    lines.append("")


def render(path: Path) -> str:
    subjects: dict[str, list[ET.Element]] = defaultdict(list)
    for node in ET.parse(path).getroot():
        if ABOUT in node.attrib:
            subjects[term(node.attrib[ABOUT])].append(node)
    subjects = dict(sorted(subjects.items()))
    class_rows, relation_rows, value_rows, individual_rows, source_rows = [], [], [], [], []
    for name, nodes in subjects.items():
        declarations = types(nodes)
        label = literal(nodes, "rdfs:label", "dcterms:title")
        definition = literal(nodes, "skos:definition", "rdfs:comment")
        code = f"\x60{name}\x60"
        if "owl:Class" in declarations:
            class_rows.append((code, label, links(nodes, "rdfs:subClassOf"), definition))
        for kind, rows in (("owl:ObjectProperty", relation_rows), ("owl:DatatypeProperty", value_rows)):
            if kind in declarations:
                rows.append((code, label, links(nodes, "rdfs:domain"), links(nodes, "rdfs:range"), definition))
        if "owl:NamedIndividual" in declarations:
            instance_types = declarations - {"owl:NamedIndividual"}
            individual_rows.append((code, label, ", ".join(f"\x60{t}\x60" for t in sorted(instance_types))))
            if instance_types & {"psq:Dataset", "psq:SourceArtifact", "psq:TheorySource"}:
                url = literal(nodes, "psq:sourceUrl")
                source_rows.append((code, literal(nodes, "dcterms:title", "rdfs:label"),
                                    literal(nodes, "psq:evidenceCategory"),
                                    literal(nodes, "dcterms:publisher"), url,
                                    literal(nodes, "psq:verificationStatus")))

    lines = [
        "# PSQ-SCO v9.1 term and source reference", "",
        "This index is generated from the bundled OWL. See [Ontology and data sources](ONTOLOGY_AND_SOURCES.md)",
        "for the four modules, how the engine uses the ontology, and how to obtain or replace inputs.", "",
        "The table lists named parents, domains and ranges; inspect the OWL for restrictions and anonymous expressions.",
        "A blank entry means that the indexed annotation is not declared, not that the term has no semantics.", "",
        f"## Classes ({len(class_rows)})", "",
    ]
    table(lines, ("Class", "Label", "Named parents", "Meaning in the OWL"), class_rows)
    for title, rows in (("Object properties", relation_rows), ("Datatype properties", value_rows)):
        lines.extend((f"## {title} ({len(rows)})", ""))
        table(lines, ("Property", "Label", "Declared domain", "Declared range", "Purpose"), rows)
    lines.extend((f"## Named individuals ({len(individual_rows)})", ""))
    table(lines, ("Identifier", "Label", "Declared classes"), individual_rows)
    lines.extend((f"## Evidence sources and datasets ({len(source_rows)})", "",
                  "URLs and verification statuses below are the ontology's metadata. A citation is not a claim",
                  "that the referenced work was ingested as a corpus or cleared for redistribution.", ""))
    table(lines, ("ID", "Title", "Evidence role", "Recorded publisher", "Recorded URL", "Status"), source_rows)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the generated Markdown without changing files.")
    args = parser.parse_args()
    text = render(ontology_path())
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print("FAIL: docs/ONTOLOGY_REFERENCE.md is out of date")
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8", newline="\n")
    print("PASS: ontology term and source reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
