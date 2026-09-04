#!/usr/bin/env python3
"""Validate MilkboxViewer source sheets and an optional standardized pet-v2 atlas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from milkbox_spec import (
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    ATLAS_ROWS,
    COLS,
    MAX_ATLAS_BYTES,
    MAX_UPLOAD_BYTES,
    SHEET_HEIGHT,
    SHEET_ROWS,
    SHEET_WIDTH,
    STATES,
)


def has_alpha(image: Image.Image) -> bool:
    return image.mode in {"RGBA", "LA"} or "transparency" in image.info


def inspect_cells(image: Image.Image, rows: int, result: dict) -> None:
    rgba = image.convert("RGBA")
    row_blank: list[int] = []
    edge_cells: list[str] = []

    for row in range(rows):
        populated = 0
        top = round(row * rgba.height / rows)
        bottom = round((row + 1) * rgba.height / rows)
        for col in range(COLS):
            left = round(col * rgba.width / COLS)
            right = round((col + 1) * rgba.width / COLS)
            alpha = rgba.crop((left, top, right, bottom)).getchannel("A")
            if alpha.getbbox() is None:
                continue
            populated += 1
            width, height = alpha.size
            touches = (
                alpha.crop((0, 0, width, 1)).getbbox()
                or alpha.crop((0, height - 1, width, height)).getbbox()
                or alpha.crop((0, 0, 1, height)).getbbox()
                or alpha.crop((width - 1, 0, width, height)).getbbox()
            )
            if touches:
                edge_cells.append(f"r{row + 1}c{col + 1}")
        if populated == 0:
            row_blank.append(row + 1)

    if row_blank:
        result["warnings"].append(f"fully blank rows: {row_blank}")
    if edge_cells:
        result["warnings"].append(
            "visible pixels touch uniform cell edges; inspect for clipping/cross-cell content: "
            + ", ".join(edge_cells[:20])
            + (" …" if len(edge_cells) > 20 else "")
        )


def inspect_hidden_rgb(image: Image.Image, result: dict) -> None:
    rgba = image.convert("RGBA")
    residue = 0
    for red, green, blue, alpha in rgba.getdata():
        if alpha == 0 and (red or green or blue):
            residue += 1
            if residue >= 100:
                break
    if residue:
        result["warnings"].append("fully transparent pixels retain hidden RGB residue")


def inspect_file(path: Path, kind: str) -> dict:
    expected = (SHEET_WIDTH, SHEET_HEIGHT) if kind.startswith("sheet") else (ATLAS_WIDTH, ATLAS_HEIGHT)
    rows = SHEET_ROWS if kind.startswith("sheet") else ATLAS_ROWS
    max_bytes = MAX_UPLOAD_BYTES if kind.startswith("sheet") else MAX_ATLAS_BYTES
    result = {
        "kind": kind,
        "path": str(path.resolve()),
        "errors": [],
        "warnings": [],
    }

    if not path.is_file():
        result["errors"].append("file does not exist")
        return result

    size = path.stat().st_size
    result["bytes"] = size
    if size > max_bytes:
        result["errors"].append(f"file exceeds {max_bytes // (1024 * 1024)} MiB limit")

    try:
        with Image.open(path) as source:
            source.load()
            image = source.copy()
            image_format = (source.format or "").upper()
    except Exception as exc:
        result["errors"].append(f"cannot decode image: {exc}")
        return result

    result.update({"format": image_format, "mode": image.mode, "width": image.width, "height": image.height})
    if image_format not in {"PNG", "WEBP"}:
        result["errors"].append("format must be PNG or WebP")
    if not has_alpha(image):
        result["errors"].append("image has no alpha-capable mode")
    else:
        alpha = image.convert("RGBA").getchannel("A")
        extrema = alpha.getextrema()
        if extrema[0] > 0:
            result["errors"].append("image contains no fully transparent pixels")

    if image.size != expected:
        if kind.startswith("sheet"):
            result["warnings"].append(
                f"nonstandard sheet size {image.width}x{image.height}; preferred size is {expected[0]}x{expected[1]} and MilkboxViewer cut lines must be confirmed"
            )
        else:
            result["errors"].append(
                f"atlas size must be {expected[0]}x{expected[1]}, found {image.width}x{image.height}"
            )

    inspect_cells(image, rows, result)
    inspect_hidden_rgb(image, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet1", type=Path, required=True)
    parser.add_argument("--sheet2", type=Path, required=True)
    parser.add_argument("--atlas", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    files = [inspect_file(args.sheet1, "sheet1"), inspect_file(args.sheet2, "sheet2")]
    if args.atlas:
        files.append(inspect_file(args.atlas, "atlas"))

    report = {
        "ok": not any(item["errors"] for item in files),
        "contract": {
            "columns": COLS,
            "sheet_rows": SHEET_ROWS,
            "atlas_rows": ATLAS_ROWS,
            "states": STATES,
        },
        "files": files,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

