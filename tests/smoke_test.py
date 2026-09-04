#!/usr/bin/env python3
"""End-to-end smoke test for the deterministic MilkboxViewer tooling."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "reading-writing",
    "rubbing",
    "washing",
    "examining",
    "resting",
    "success",
    "failed",
    "grabbed",
]
def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, capture_output=True, text=True)


def run_expect_failure(*args: str) -> None:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    assert result.returncode != 0, f"command unexpectedly succeeded: {' '.join(args)}"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="milkbox-pet-smoke-") as temporary:
        temp = Path(temporary)
        rows_dir = temp / "rows"
        output_dir = temp / "delivery"
        standardized_dir = temp / "standardized"
        repaired_dir = temp / "repaired"
        previews_dir = temp / "previews"
        rows_dir.mkdir()

        for state_index, state in enumerate(STATES):
            row = Image.new("RGBA", (1536, 208), (0, 0, 0, 0))
            draw = ImageDraw.Draw(row)
            for frame in range(8):
                left = frame * 192 + 44 + frame % 3
                top = 42 + (frame + state_index) % 5
                color = (60 + state_index * 10, 100 + frame * 10, 180, 255)
                draw.rounded_rectangle((left, top, left + 96, top + 146), radius=24, fill=color)
            row.save(rows_dir / f"{state}.png")

        run(str(SCRIPTS / "compose_from_rows.py"), "--rows-dir", str(rows_dir), "--output-dir", str(output_dir))
        sheet1 = output_dir / "milkbox-pet-sheet-1.png"
        sheet2 = output_dir / "milkbox-pet-sheet-2.png"
        atlas = output_dir / "milkbox-pet-v2-atlas.png"
        run(
            str(SCRIPTS / "validate_pet_images.py"),
            "--sheet1",
            str(sheet1),
            "--sheet2",
            str(sheet2),
            "--atlas",
            str(atlas),
        )
        run(
            str(SCRIPTS / "render_previews.py"),
            "--sheet1",
            str(sheet1),
            "--sheet2",
            str(sheet2),
            "--output-dir",
            str(previews_dir),
        )

        assert Image.open(sheet1).size == (1536, 1248)
        assert Image.open(sheet2).size == (1536, 1248)
        assert Image.open(atlas).size == (1536, 2496)
        assert len(list(previews_dir.glob("*.gif"))) == 12
        # Fast/Mixed path: accept two uniformly gridded sheets at another size,
        # then standardize them and build the atlas in one operation.
        raw_sheet1 = temp / "raw-sheet-1.png"
        raw_sheet2 = temp / "raw-sheet-2.png"
        with Image.open(sheet1) as image:
            image.resize((1200, 960)).save(raw_sheet1)
        with Image.open(sheet2) as image:
            image.resize((1200, 960)).save(raw_sheet2)
        run(
            str(SCRIPTS / "standardize_sheets.py"),
            "--sheet1",
            str(raw_sheet1),
            "--sheet2",
            str(raw_sheet2),
            "--output-dir",
            str(standardized_dir),
        )
        standardized_sheet1 = standardized_dir / "milkbox-pet-sheet-1.png"
        standardized_sheet2 = standardized_dir / "milkbox-pet-sheet-2.png"
        standardized_atlas = standardized_dir / "milkbox-pet-v2-atlas.png"
        assert Image.open(standardized_sheet1).size == (1536, 1248)
        assert Image.open(standardized_sheet2).size == (1536, 1248)
        assert Image.open(standardized_atlas).size == (1536, 2496)

        # Mixed repair path: replace only the requested action row and reject a
        # row assigned to the wrong delivery sheet.
        replacement = temp / "waving-replacement.png"
        replacement_image = Image.new("RGBA", (1536, 208), (0, 0, 0, 0))
        replacement_draw = ImageDraw.Draw(replacement_image)
        for frame in range(8):
            left = frame * 192 + 32
            replacement_draw.ellipse((left, 24, left + 128, 184), fill=(255, 0, 180, 255))
        replacement_image.save(replacement)

        repaired_sheet1 = repaired_dir / "milkbox-pet-sheet-1.png"
        run(
            str(SCRIPTS / "replace_sheet_row.py"),
            "--sheet",
            str(standardized_sheet1),
            "--sheet-number",
            "1",
            "--state",
            "waving",
            "--replacement",
            str(replacement),
            "--output",
            str(repaired_sheet1),
        )
        run_expect_failure(
            str(SCRIPTS / "replace_sheet_row.py"),
            "--sheet",
            str(standardized_sheet1),
            "--sheet-number",
            "1",
            "--state",
            "failed",
            "--replacement",
            str(replacement),
            "--output",
            str(repaired_dir / "must-not-exist.png"),
        )

        with Image.open(standardized_sheet1) as before_source, Image.open(repaired_sheet1) as after_source:
            before = before_source.convert("RGBA")
            after = after_source.convert("RGBA")
        waving_top = 3 * 208
        assert ImageChops.difference(
            before.crop((0, waving_top, 1536, waving_top + 208)),
            after.crop((0, waving_top, 1536, waving_top + 208)),
        ).getbbox() is not None
        assert ImageChops.difference(
            before.crop((0, 0, 1536, waving_top)),
            after.crop((0, 0, 1536, waving_top)),
        ).getbbox() is None
        assert ImageChops.difference(
            before.crop((0, waving_top + 208, 1536, 1248)),
            after.crop((0, waving_top + 208, 1536, 1248)),
        ).getbbox() is None

        # Rebuild and validate all deliverables after a row repair.
        run(
            str(SCRIPTS / "standardize_sheets.py"),
            "--sheet1",
            str(repaired_sheet1),
            "--sheet2",
            str(standardized_sheet2),
            "--output-dir",
            str(repaired_dir),
        )
        run(
            str(SCRIPTS / "validate_pet_images.py"),
            "--sheet1",
            str(repaired_dir / "milkbox-pet-sheet-1.png"),
            "--sheet2",
            str(repaired_dir / "milkbox-pet-sheet-2.png"),
            "--atlas",
            str(repaired_dir / "milkbox-pet-v2-atlas.png"),
        )

    print("milkbox-pet smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
