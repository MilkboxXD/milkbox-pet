"""Behavioral regressions for uneven generated poses and straight-cut delivery."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from normalize_generated_rows import separated_frames, pack_frames, normalize_manifest, load_source
from compose_from_rows import load_normalized_row
from validate_pet_images import inspect_cells, inspect_file
from render_previews import extract_rows, render_cut_overlay
from standardize_sheets import normalize_sheet
from milkbox_spec import STATES, SHEET_1_STATES


def row_art(count=6):
    row = Image.new("RGBA", (1100, 190))
    draw = ImageDraw.Draw(row)
    for index in range(count):
        x = 20 + index * 120 + (index % 3) * 7
        draw.rectangle((x, 40 + index * 3, x + 65, 160), fill=(40, 90 + index, 160, 255))
    return row


def run_script(name, *args, succeeds=True):
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / name), *map(str, args)],
                            capture_output=True, text=True)
    if (result.returncode == 0) != succeeds:
        raise AssertionError(result.stdout + result.stderr)
    return result


class AlignmentTests(unittest.TestCase):
    def test_six_uneven_frames_keep_common_scale_and_trailing_slots(self):
        row = pack_frames(separated_frames(row_art(), 6))
        widths = []
        for index in range(8):
            bbox = row.crop((index * 192, 0, (index + 1) * 192, 208)).getchannel("A").getbbox()
            if index < 6:
                widths.append(bbox[2] - bbox[0])
            else:
                self.assertIsNone(bbox)
        self.assertEqual(widths, [66] * 6)
        report = {"errors": [], "warnings": []}
        inspect_cells(row, 1, report, strict=True, padding=8, expected_counts=[6])
        self.assertEqual(report["errors"], [])

    def test_wrong_count_and_connected_poses_are_rejected(self):
        with self.assertRaises(ValueError):
            separated_frames(row_art(6), 8)
        row = row_art(2)
        ImageDraw.Draw(row).line((40, 100, 170, 100), fill=(1, 2, 3, 1))
        with self.assertRaises(ValueError):
            separated_frames(row, 2)
        with self.assertRaises(ValueError):
            separated_frames(row, 2, cuts=[120])

    def test_reviewed_cut_keeps_disconnected_prop_and_faint_pixels(self):
        row = row_art(2)
        ImageDraw.Draw(row).rectangle((95, 90, 101, 96), fill=(100, 60, 30, 1))
        with self.assertRaises(ValueError):
            separated_frames(row, 2)
        frames = separated_frames(row, 2, cuts=[120])
        self.assertEqual(sum(f.getchannel("A").histogram()[1] for f, _ in frames), 49)
        self.assertEqual(sum(sum(f.getchannel("A").histogram()[1:]) for f, _ in frames),
                         sum(row.getchannel("A").histogram()[1:]))

    def test_anchors_preserve_vertical_motion(self):
        row = Image.new("RGBA", (300, 200))
        draw = ImageDraw.Draw(row)
        draw.rectangle((30, 70, 70, 140), fill="red")
        draw.rectangle((180, 50, 220, 120), fill="red")
        result = pack_frames(separated_frames(row, 2), anchors=[[50, 180], [200, 180]])
        first = result.crop((0, 0, 192, 208)).getchannel("A").getbbox()
        second = result.crop((192, 0, 384, 208)).getchannel("A").getbbox()
        self.assertEqual(first[1] - second[1], 20)
        self.assertEqual(first[3] - second[3], 20)

    def test_bad_counts_cuts_and_source_edges_fail(self):
        for count in [0, 9, True, 6.0]:
            with self.assertRaises(ValueError):
                separated_frames(row_art(), count)
        with self.assertRaises(ValueError):
            separated_frames(row_art(2), 2, cuts=[-1])
        row = row_art(1)
        row.putpixel((0, 100), (10, 20, 30, 1))
        with self.assertRaises(ValueError):
            separated_frames(row, 1)

    def test_strict_cells_reject_margin_blank_gap_and_count(self):
        valid = pack_frames(separated_frames(row_art(2), 2))
        for variant in ["margin", "blank", "gap", "count"]:
            row = valid.copy()
            expected = [2]
            if variant == "margin":
                row.putpixel((191, 50), (20, 30, 40, 1))
            elif variant == "blank":
                row = Image.new("RGBA", row.size)
            elif variant == "gap":
                row.paste((0, 0, 0, 0), (0, 0, 192, 208))
            else:
                expected = [3]
            report = {"errors": [], "warnings": []}
            inspect_cells(row, 1, report, strict=True, padding=8, expected_counts=expected)
            self.assertTrue(report["errors"], variant)

    def test_nontransparent_sources_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for suffix in ["png", "jpg"]:
                path = Path(temp) / f"source.{suffix}"
                Image.new("RGB", (100, 100), "white").save(path)
                with self.assertRaises(ValueError):
                    load_source(path)

    def test_manifest_rejects_uncovered_art_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = row_art(2)
            source.save(folder / "source.png")
            manifest = folder / "extract.json"
            manifest.write_text(json.dumps({"rows": [{"state": "idle", "source": "source.png",
                                                       "box": [0, 0, 120, 190], "frame_count": 1}]}))
            with self.assertRaises(ValueError):
                normalize_manifest(manifest, folder / "output", 8)
            self.assertFalse((folder / "output").exists())

    def test_full_mixed_pipeline_and_preserved_registration(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            rows = []
            counts = {state: (6 if index % 3 == 0 else 8) for index, state in enumerate(STATES)}
            for sheet_index in range(2):
                source = Image.new("RGBA", (1100, 1200))
                for row_index in range(6):
                    state = STATES[sheet_index * 6 + row_index]
                    source.paste(row_art(counts[state]), (0, row_index * 200))
                    rows.append({"state": state, "source": f"source-{sheet_index}.png",
                                 "box": [0, row_index * 200, 1100, (row_index + 1) * 200],
                                 "frame_count": counts[state]})
                source.save(folder / f"source-{sheet_index}.png")
            with self.assertRaises(ValueError):
                normalize_sheet(folder / "source-0.png", None, 18)
            manifest = folder / "extract.json"
            manifest.write_text(json.dumps({"rows": rows}))
            plan = folder / "counts.json"
            plan.write_text(json.dumps(counts))
            normalized, delivery, previews = folder / "rows", folder / "delivery", folder / "previews"
            run_script("normalize_generated_rows.py", "--manifest", manifest, "--output-dir", normalized)
            run_script("compose_from_rows.py", "--rows-dir", normalized, "--output-dir", delivery)
            sheet1, sheet2, atlas = [delivery / f"milkbox-pet-{name}.png" for name in ["sheet-1", "sheet-2", "v2-atlas"]]
            run_script("validate_pet_images.py", "--sheet1", sheet1, "--sheet2", sheet2, "--atlas", atlas,
                       "--strict", "--frame-counts", plan)
            with Image.open(normalized / "idle.png") as row, Image.open(sheet1) as sheet:
                self.assertEqual(row.tobytes(), sheet.crop((0, 0, 1536, 208)).tobytes())
                frames = load_normalized_row(normalized / "idle.png", None, 18, 8)
                self.assertEqual(frames[0].tobytes(), row.crop((0, 0, 192, 208)).tobytes())
            run_script("render_previews.py", "--sheet1", sheet1, "--sheet2", sheet2, "--output-dir", previews)
            self.assertEqual(len(list(previews.glob("*.gif"))), 12)
            self.assertEqual(len(list(previews.glob("*-cut-overlay.png"))), 2)
            self.assertEqual(len(extract_rows(sheet1, SHEET_1_STATES)["idle"]), 6)
            # Atlas must correspond to these exact sheets, even if counts and sizes match.
            with Image.open(atlas) as image:
                changed = image.copy()
            changed.putpixel((60, 100), (200, 30, 50, 255))
            changed.save(atlas)
            run_script("validate_pet_images.py", "--sheet1", sheet1, "--sheet2", sheet2,
                       "--atlas", atlas, "--strict", "--frame-counts", plan, succeeds=False)


if __name__ == "__main__":
    unittest.main()
