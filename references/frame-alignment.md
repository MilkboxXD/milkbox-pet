# Frame extraction and straight-cut alignment

Generated images are source artwork. Before delivery, extract complete frames and pack them into deterministic cells. A prompt cannot certify source alignment.

## Prompt constraints

Describe continuous left-to-right animation, and also specify that every row shares the same eight reserved x positions. Keep each complete pose, tail and prop inside its position with transparent gutters. Six-frame actions occupy positions 1–6; positions 7–8 stay transparent. Do not spread six frames across the full width or draw the guides. These constraints reduce errors; extraction and QA remain mandatory.

Use original transparent PNG/WebP sources. JPEG and drawn checkerboards have no usable alpha. An explicitly chosen flat chroma key may be removed with `--chroma-key RRGGBB --chroma-tolerance 18`; check fur and accessory edges afterward. Do not threshold away character colors or faint pixels to make a cut appear safe.

## Record the approved motion plan

Create `frame-counts.json` as a JSON object mapping all twelve exact state names to their approved useful frame counts (integers 1–8). Counts include intentional hold frames. Compare extracted counts to this plan; do not silently lower the count to accommodate missing artwork.

If an action deliberately jumps, bobs, floats or dangles, record registration anchors for each frame relative to a shared ground or suspension reference. Automatic bottom alignment is suitable only for grounded poses. Inspect body scale across actions against the canonical character; the program cannot identify anatomical landmarks automatically.

## Mixed / Fast: reviewed source row boxes

Inspect each generated sheet and create an extraction manifest. Row boxes follow the actual source layout, not assumed equal sixths. Account for every visible pixel in each referenced source, including all six actions. Coordinates use source pixels with exclusive right/bottom edges. Paths are relative to the manifest.

Minimal schema example (illustrative one-row source; supply all twelve states for a full delivery):

```json
{
  "rows": [
    {
      "state": "idle",
      "source": "sources/idle.png",
      "box": [0, 0, 1200, 260],
      "frame_count": 6
    }
  ]
}
```

For a full sheet, several entries reference the same source with different, non-overlapping row boxes. For a standalone strip, omit `box` to use the entire source.

Run:

```powershell
python scripts/normalize_generated_rows.py --manifest extraction.json --output-dir normalized-rows
python scripts/compose_from_rows.py --rows-dir normalized-rows --output-dir delivery
```

The extractor finds completely transparent vertical gutters inside each row. If there are too many spans (for example, a disconnected prop), add `cuts`, an increasing list of `frame_count - 1` x coordinates **relative to the cropped row**. Visually confirm each resulting span contains one complete pose and its own props. Both sides of every cut must be transparent. Never force a valley cut through nontransparent pixels.

For intentional motion, add `anchors`, one `[x, y]` registration point per frame, also in cropped-row coordinates. Every point identifies the same ground/suspension reference; do not attach a ground anchor to an airborne foot. The packer uses a common scale and translation relative to these anchors, preserving the intended motion. With no anchors it aligns each pose's bottom-center; do not use that fallback for airborne actions.

The command rejects unexpected counts, overlapping row boxes, pixels outside the reviewed boxes, empty declared frames, cropped source edges and cuts through visible art. Ambiguous or merged poses require a reviewed extraction or row regeneration. It never invents missing artwork. In Mixed, repair the failed row; in Fast, use the existing whole-sheet regeneration / explicit mode-switch policy.

## Precision / individual repair rows

For separated source strips named `<state>.png` or `<state>.webp`:

```powershell
python scripts/normalize_generated_rows.py --input-dir source-rows --frame-counts frame-counts.json --output-dir normalized-rows
python scripts/compose_from_rows.py --rows-dir normalized-rows --output-dir delivery
```

Use the manifest route when strips need reviewed cuts or anchors. For a one-row repair, a manifest/counts object may contain that state only; merge the approved count into the complete twelve-state plan before final validation. Always replace with the **normalized** row:

```powershell
python scripts/replace_sheet_row.py --sheet delivery/milkbox-pet-sheet-1.png --sheet-number 1 --state waving --replacement normalized-rows/waving.png --output repaired-sheet-1.png
```

## Fixed layout and acceptance

- Normalized rows are exactly `1536x208`, with eight `192x208` cells. Only the approved leading cells contain frames; trailing cells stay fully transparent.
- All frames in a row use one scale. Composition and row replacement preserve normalized pixels and registration; they do not independently recenter or resize each pose.
- Maintain at least 8 transparent pixels at every cell edge. The extractor reserves a little additional space for rounding.
- `standardize_sheets.py` is only for already uniformly aligned sheets or rebuilding the atlas after repair. It checks cell boundaries before any equal slicing and preserves aspect ratio when resizing. It is not the first operation on unaligned generated artwork.
- Technical checks cannot prove one complete character per cell, correct props, action semantics, or consistent identity. Review both fixed-cut overlays and all twelve GIFs.

```powershell
python scripts/validate_pet_images.py --sheet1 delivery/milkbox-pet-sheet-1.png --sheet2 delivery/milkbox-pet-sheet-2.png --atlas delivery/milkbox-pet-v2-atlas.png --strict --frame-counts frame-counts.json --json-out validation.json
python scripts/render_previews.py --sheet1 delivery/milkbox-pet-sheet-1.png --sheet2 delivery/milkbox-pet-sheet-2.png --output-dir previews
```

Inspect `previews/sheet-1-cut-overlay.png` and `previews/sheet-2-cut-overlay.png`. Red lines mark the fixed cuts every 192 pixels horizontally and 208 vertically; inner outlines mark 8-pixel margins. Every visible character and prop must fit one cell without fragments. Overlays are QA artifacts, never delivery spritesheets. GIF previews omit only unused trailing slots so valid short actions do not blink out; internal blank frames fail.

`--strict` requires standard dimensions and safe margins for both sheets and the atlas. Whole blank actions, internal empty cells, incorrect approved counts and atlas/sheet pixel mismatches fail validation. Nonstandard user uploads can be inspected without `--strict`, but that report is not final acceptance for images produced by this skill.
