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


def inspect_cells(image: Image.Image, rows: int, result: dict, strict: bool = False,
                  padding: int = 1, expected_counts: list[int] | None = None) -> None:
    rgba = image.convert("RGBA")
    problems = []
    observed = []
    for row in range(rows):
        present = []
        top = round(row * rgba.height / rows)
        bottom = round((row + 1) * rgba.height / rows)
        for col in range(COLS):
            left = round(col * rgba.width / COLS)
            right = round((col + 1) * rgba.width / COLS)
            alpha = rgba.crop((left, top, right, bottom)).getchannel("A")
            bbox = alpha.getbbox()
            present.append(bbox is not None)
            if bbox is not None:
                if (bbox[0] < padding or bbox[1] < padding
                        or bbox[2] > alpha.width - padding or bbox[3] > alpha.height - padding):
                    problems.append(f"r{row + 1}c{col + 1}: visible pixels violate {padding}px cell margin")
        populated = sum(present)
        observed.append(populated)
        if populated == 0:
            problems.append(f"r{row + 1}: fully blank action row")
        elif present != [True] * populated + [False] * (COLS - populated):
            problems.append(f"r{row + 1}: empty cells must be trailing")
        if expected_counts is not None and populated != expected_counts[row]:
            problems.append(f"r{row + 1}: expected {expected_counts[row]} frames, found {populated}")
    result["frame_counts"] = observed
    result["errors" if strict else "warnings"].extend(problems)


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


def inspect_file(path: Path, kind: str, strict: bool = False,
                 padding: int = 8, expected_counts: list[int] | None = None) -> dict:
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
        if kind.startswith("sheet") and not strict:
            result["warnings"].append(
                f"nonstandard sheet size {image.width}x{image.height}; preferred size is {expected[0]}x{expected[1]} and MilkboxViewer cut lines must be confirmed"
            )
        else:
            result["errors"].append(
                f"{kind} size must be {expected[0]}x{expected[1]}, found {image.width}x{image.height}"
            )

    inspect_cells(image, rows, result, strict=strict or image.size == expected,
                  padding=padding if strict else 1, expected_counts=expected_counts)
    inspect_hidden_rgb(image, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet1", type=Path, required=True)
    parser.add_argument("--sheet2", type=Path, required=True)
    parser.add_argument("--atlas", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--strict", action="store_true", help="require standard dimensions and safe margins on all delivery files")
    parser.add_argument("--padding", type=int, default=8)
    parser.add_argument("--frame-counts", type=Path, help="approved JSON counts for all twelve states")
    args = parser.parse_args()

    if not 1 <= args.padding < 96:
        parser.error("padding must be between 1 and 95")
    counts = None
    if args.frame_counts:
        try:
            mapping = json.loads(args.frame_counts.read_text(encoding="utf-8"))
            if not isinstance(mapping, dict) or set(mapping) != set(STATES):
                raise ValueError("frame-counts must contain exactly the twelve state names")
            counts = [mapping[state] for state in STATES]
            if any(type(n) is not int or not 1 <= n <= COLS for n in counts):
                raise ValueError("approved counts must be integers from 1 to 8")
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    files = [inspect_file(args.sheet1, "sheet1", args.strict, args.padding, counts[:6] if counts else None),
             inspect_file(args.sheet2, "sheet2", args.strict, args.padding, counts[6:] if counts else None)]
    if args.atlas:
        files.append(inspect_file(args.atlas, "atlas", args.strict, args.padding, counts))
        if not any(item["errors"] for item in files):
            with Image.open(args.sheet1) as s1, Image.open(args.sheet2) as s2, Image.open(args.atlas) as atlas:
                if s1.size == (SHEET_WIDTH, SHEET_HEIGHT) and s2.size == (SHEET_WIDTH, SHEET_HEIGHT):
                    combined = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
                    combined.paste(s1.convert("RGBA"), (0, 0))
                    combined.paste(s2.convert("RGBA"), (0, SHEET_HEIGHT))
                    from PIL import ImageChops
                    diff = ImageChops.difference(combined, atlas.convert("RGBA"))
                    if any(channel.getbbox() is not None for channel in diff.split()):
                        files[-1]["errors"].append("atlas pixels do not match the two delivery sheets")

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


