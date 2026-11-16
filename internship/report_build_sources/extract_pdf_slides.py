from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(r".")
OUT = ROOT / "_internship_report_work" / "slide_text"
OUT.mkdir(parents=True, exist_ok=True)


def safe_stem(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_")
    return stem


manifest = []
for pdf_path in sorted(ROOT.glob("*.pdf"), key=lambda p: p.name.lower()):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            pages.append(
                {
                    "page": page_number,
                    "width": page.width,
                    "height": page.height,
                    "text": text.strip(),
                }
            )

    stem = safe_stem(pdf_path.name)
    json_path = OUT / f"{stem}.json"
    txt_path = OUT / f"{stem}.txt"
    json_path.write_text(
        json.dumps(
            {
                "source": str(pdf_path),
                "page_count": len(pages),
                "pages": pages,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    txt_path.write_text(
        "\n\n".join(
            f"===== SLIDE {p['page']} =====\n{p['text']}" for p in pages
        ),
        encoding="utf-8",
    )
    manifest.append(
        {
            "source": str(pdf_path),
            "page_count": len(pages),
            "text": str(txt_path),
            "json": str(json_path),
        }
    )

(OUT / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(manifest, ensure_ascii=False, indent=2))
