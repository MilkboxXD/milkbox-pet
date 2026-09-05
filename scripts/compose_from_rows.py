#!/usr/bin/env python3
"""Compose twelve eight-slot row strips into MilkboxViewer delivery sheets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from milkbox_spec import (
    ATLAS_HEIGHT,
    ATLAS_WIDTH,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLS,
    SHEET_1_STATES,
    SHEET_2_STATES,
    SHEET_HEIGHT,
    SHEET_WIDTH,
    STATES,
)


def parse_hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("chroma key must be RRGGBB or #RRGGBB")
    try:
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("chroma key must contain hexadecimal digits") from exc


def remove_chroma(image: Image.Image, key: tuple[int, int, int], tolerance: int) -> Image.Image:
    rgba = image.convert("RGBA")
    cleaned: list[tuple[int, int, int, int]] = []
    kr, kg, kb = key
    for red, green, blue, alpha in rgba.getdata():
        if max(abs(red - kr), abs(green - kg), abs(blue - kb)) <= tolerance:
            cleaned.append((0, 0, 0, 0))
        elif alpha == 0:
            cleaned.append((0, 0, 0, 0))
        else:
            cleaned.append((red, green, blue, alpha))
    rgba.putdata(cleaned)
    return rgba


def find_row_file(rows_dir: Path, state: str) -> Path:
    matches = [path for suffix in (".png", ".webp") if (path := rows_dir / f"{state}{suffix}").is_file()]
    if not matches:
        raise FileNotFoundError(f"missing row strip for {state}: expected {state}.png or {state}.webp")
    return matches[0]


def slot_bounds(width: int, index: int) -> tuple[int, int]:
    return round(index * width / COLS), round((index + 1) * width / COLS)


def load_normalized_row(
    path: Path,
    chroma_key: tuple[int, int, int] | None,
    chroma_tolerance: int,
    padding: int,
) -> list[Image.Image]:
    """Compose only already registered rows; preserve frame positions and scale."""
    from validate_pet_images import inspect_cells

    with Image.open(path) as source:
        row = source.convert("RGBA")
    if chroma_key is not None:
        row = remove_chroma(row, chroma_key, chroma_tolerance)
    if row.size != (SHEET_WIDTH, CELL_HEIGHT):
        raise ValueError(f"{path}: normalize_generated_rows.py must first create a 1536x208 row")
    report = {"errors": [], "warnings": []}
    inspect_cells(row, 1, report, strict=True, padding=max(8, padding))
    if report["errors"]:
        raise ValueError(f"{path}: " + "; ".join(report["errors"]))
    return [row.crop((i * CELL_WIDTH, 0, (i + 1) * CELL_WIDTH, CELL_HEIGHT)) for i in range(COLS)]


def build_sheet(rows: list[list[Image.Image]]) -> Image.Image:
    sheet = Image.new("RGBA", (SHEET_WIDTH, SHEET_HEIGHT), (0, 0, 0, 0))
    for row_index, frames in enumerate(rows):
        for column, frame in enumerate(frames):
            sheet.alpha_composite(frame, (column * CELL_WIDTH, row_index * CELL_HEIGHT))
    return sheet


def save_png(image: Image.Image, path: Path) -> None:
    normalized = Image.new("RGBA", image.size, (0, 0, 0, 0))
    normalized.alpha_composite(image)
    normalized.save(path, format="PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chroma-key", type=parse_hex_color)
    parser.add_argument("--chroma-tolerance", type=int, default=18)
    parser.add_argument("--padding", type=int, default=8)
    args = parser.parse_args()

    if not 0 <= args.chroma_tolerance <= 255:
        parser.error("--chroma-tolerance must be between 0 and 255")
    if not 0 <= args.padding < min(CELL_WIDTH, CELL_HEIGHT) // 2:
        parser.error("--padding is outside the valid cell range")

    rows: dict[str, list[Image.Image]] = {}
    for state in STATES:
        path = find_row_file(args.rows_dir, state)
        rows[state] = load_normalized_row(path, args.chroma_key, args.chroma_tolerance, args.padding)

    sheet1 = build_sheet([rows[state] for state in SHEET_1_STATES])
    sheet2 = build_sheet([rows[state] for state in SHEET_2_STATES])
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

