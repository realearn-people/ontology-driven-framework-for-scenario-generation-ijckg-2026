import json
from pathlib import Path

import pdfplumber


PDF = Path(
    r"_internship_report_work/render_verified"
    r"\Research_Internship_Report_Chanphot_Wongtaweesup_PSQ_SCO.pdf"
)
TARGETS = [
    "Executive Summary",
    "1. Internship Timeline and Linked Work",
    "2. Complete Work: Ontology, Engine Integration, and Evaluation",
    "3. Internship Results: Ontology, Evaluation, and Paper",
    "References",
    "Appendix A. Dated Slide-Deck Evidence",
    "Appendix B. Project Artifact Inventory",
    "Appendix C. Validation and Evaluation Evidence Matrix",
    "Appendix D. Close-out Checklist to 6 August 2026",
]


def normalized(text: str) -> str:
    return " ".join((text or "").replace("\u00ad", "").split())


with pdfplumber.open(PDF) as pdf:
    page_text = [normalized(page.extract_text() or "") for page in pdf.pages]

contents_page = next(
    index + 1
    for index, text in enumerate(page_text)
    if "Contents Section Page" in text
)

result = {}
for target in TARGETS:
    needle = normalized(target)
    matches = [index + 1 for index, text in enumerate(page_text) if needle in text]
    if not matches:
        raise SystemExit(f"Heading not found in rendered PDF: {target}")
    if target == "Executive Summary":
        result[target] = matches[0]
    else:
        post_contents = [page for page in matches if page > contents_page]
        if not post_contents:
            raise SystemExit(f"Body heading not found after contents page: {target}")
        result[target] = post_contents[0]

print(json.dumps(result, indent=2, ensure_ascii=False))
