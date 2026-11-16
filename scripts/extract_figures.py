#!/usr/bin/env python3
"""Extract paper figures with a local pdffigures2 JAR and preserve its evidence."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def normalize_items(raw: object, figures: Path, report_root: Path) -> list[dict]:
    """Keep actual extractor records, including captions without image regions."""
    if isinstance(raw, list):
        entries = raw
        regionless = []
    elif isinstance(raw, dict) and isinstance(raw.get("figures"), list):
        entries = raw["figures"]
        regionless = raw.get("regionless-captions", [])
        if not isinstance(regionless, list):
            raise ValueError("pdffigures2 regionless-captions must be a list")
    else:
        raise ValueError("Expected a figure list or an object with a figures list")

    items = []
    for metadata, has_region in [
        *((entry, True) for entry in entries),
        *((entry, False) for entry in regionless),
    ]:
        if not isinstance(metadata, dict):
            raise ValueError("Each pdffigures2 record must be an object")
        item = dict(metadata)
        page = metadata.get("page")
        item["pdf_page"] = page + 1 if type(page) is int and page >= 0 else None
        item["image"] = ""
        item["status"] = "unavailable"
        if not has_region:
            item.setdefault("caption", metadata.get("text", ""))
            item["unavailable_reason"] = "pdffigures2 found a caption but no image region."
        else:
            rendered = metadata.get("renderURL")
            if not isinstance(rendered, str) or not rendered.strip():
                item["unavailable_reason"] = "pdffigures2 did not record an image path."
            else:
                image = Path(rendered)
                if not image.is_absolute():
                    image = report_root / image
                image = image.resolve()
                if not image.is_relative_to(figures):
                    item["unavailable_reason"] = "Recorded image is outside this extraction's figures directory."
                elif not image.is_file() or image.stat().st_size == 0:
                    item["unavailable_reason"] = "Recorded image is missing or empty."
                else:
                    item["image"] = image.relative_to(report_root).as_posix()
                    item["status"] = "extracted"
        items.append(item)
    return items


def extract(pdf: Path, jar: Path, java: str, out: Path, dpi: int) -> Path:
    pdf = pdf.resolve()
    jar = jar.resolve()
    out = out.resolve()
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        raise ValueError(f"PDF does not exist or is not a .pdf file: {pdf}")
    if not jar.is_file():
        raise ValueError(f"pdffigures2 JAR does not exist: {jar}")
    if out.name != "extracted":
        raise ValueError("--out must name the paper report's extracted directory")
    if dpi <= 0:
        raise ValueError("--dpi must be positive")

    figures = out / "figures"
    raw_dir = out / "pdffigures2-data"
    raw_path = raw_dir / f"{pdf.stem}.json"
    manifest_path = out / "figure_manifest.json"
    log_path = out / "pdffigures2.log"
    for existing in (manifest_path, log_path):
        if existing.exists():
            raise FileExistsError(f"Refusing to overwrite extraction evidence: {existing}")
    for directory in (raw_dir, figures):
        if directory.exists() and (not directory.is_dir() or any(directory.iterdir())):
            raise FileExistsError(f"Refusing to overwrite a nonempty extraction directory: {directory}")

    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(exist_ok=True)
    raw_dir.mkdir(exist_ok=True)
    command = [
        java,
        "-Dfile.encoding=UTF-8",
        "-jar",
        str(jar),
        str(pdf),
        "-m",
        str(figures) + os.sep,
        "-d",
        str(raw_dir) + os.sep,
        "-c",
        "-i",
        str(dpi),
    ]
    with log_path.open("x", encoding="utf-8") as log:
        log.write("Command (JSON): " + json.dumps(command, ensure_ascii=False) + "\n\n")
        log.flush()
        result = subprocess.run(
            command,
            cwd=out.parent,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode:
        raise RuntimeError(f"pdffigures2 exited with code {result.returncode}; inspect {log_path}")
    if not raw_path.is_file():
        raise RuntimeError(f"pdffigures2 produced no expected metadata at {raw_path}; inspect {log_path}")

    raw = json.loads(raw_path.read_text(encoding="utf-8-sig"))
    report_root = out.parent
    items = normalize_items(raw, figures, report_root)
    try:
        pdf_reference = pdf.relative_to(report_root).as_posix()
    except ValueError:
        pdf_reference = pdf.as_posix()
    manifest = {
        "source": "pdffigures2",
        "pdf": pdf_reference,
        "raw_metadata": raw_path.relative_to(report_root).as_posix(),
        "page_indexing": "raw page zero-based; pdf_page one-based; null means unknown",
        "items": items,
    }
    with manifest_path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(manifest, output, ensure_ascii=False, indent=2)
        output.write("\n")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--jar", type=Path, required=True, help="Existing pdffigures2 assembly JAR")
    parser.add_argument("--java", default="java", help="Java executable, optionally an absolute path")
    parser.add_argument("--out", type=Path, required=True, help="Paper report's extracted directory")
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()
    try:
        manifest = extract(args.pdf, args.jar, args.java, args.out, args.dpi)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Figure extraction failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved pdffigures2 figure manifest: {manifest}")
    print("Image existence does not establish visual correctness or complete figure coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
