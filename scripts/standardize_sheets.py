#!/usr/bin/env python3
"""Normalize two uniformly gridded 8x6 sheets and combine the pet-v2 atlas."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from compose_from_rows import parse_hex_color, remove_chroma, save_png
from milkbox_spec import (
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLS,
    SHEET_HEIGHT,
    SHEET_ROWS,
    SHEET_WIDTH,
)


def normalize_sheet(
    path: Path,
    chroma_key: tuple[int, int, int] | None,
    chroma_tolerance: int,
) -> Image.Image:
    with Image.open(path) as source:
        sheet = source.convert("RGBA")
    if chroma_key is not None:
        sheet = remove_chroma(sheet, chroma_key, chroma_tolerance)

    output = Image.new("RGBA", (SHEET_WIDTH, SHEET_HEIGHT), (0, 0, 0, 0))
    for row in range(SHEET_ROWS):
        top = round(row * sheet.height / SHEET_ROWS)
        bottom = round((row + 1) * sheet.height / SHEET_ROWS)
        for column in range(COLS):
            left = round(column * sheet.width / COLS)
            right = round((column + 1) * sheet.width / COLS)
            cell = sheet.crop((left, top, right, bottom))
            if cell.size != (CELL_WIDTH, CELL_HEIGHT):
                cell = cell.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)
            output.alpha_composite(cell, (column * CELL_WIDTH, row * CELL_HEIGHT))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet1", type=Path, required=True)
    parser.add_argument("--sheet2", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chroma-key", type=parse_hex_color)
    parser.add_argument("--chroma-tolerance", type=int, default=18)
    args = parser.parse_args()

    if not 0 <= args.chroma_tolerance <= 255:
        parser.error("--chroma-tolerance must be between 0 and 255")
    for path in (args.sheet1, args.sheet2):
        if not path.is_file():
            parser.error(f"input sheet does not exist: {path}")

    sheet1 = normalize_sheet(args.sheet1, args.chroma_key, args.chroma_tolerance)
    sheet2 = normalize_sheet(args.sheet2, args.chroma_key, args.chroma_tolerance)
    atlas = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
    atlas.alpha_composite(sheet1, (0, 0))
    atlas.alpha_composite(sheet2, (0, SHEET_HEIGHT))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "sheet1": args.output_dir / "milkbox-pet-sheet-1.png",
        "sheet2": args.output_dir / "milkbox-pet-sheet-2.png",
        "atlas": args.output_dir / "milkbox-pet-v2-atlas.png",
    }
    save_png(sheet1, outputs["sheet1"])
    save_png(sheet2, outputs["sheet2"])
    save_png(atlas, outputs["atlas"])

    print(f"sheet1={outputs['sheet1'].resolve()}")
    print(f"sheet2={outputs['sheet2'].resolve()}")
    print(f"atlas={outputs['atlas'].resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
