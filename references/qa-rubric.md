# Milkbox Pet QA Rubric

Do not accept a delivery until deterministic checks and visual inspection both pass.

## Geometry and files

- Exactly two delivery sheets, each preserving 8 columns × 6 rows.
- Preferred sheet size is `1536x1248`; nonstandard input is acceptable only for resident-center cutting and should be reported as a warning.
- Standardized atlas is exactly `1536x2496`, 8 columns × 12 rows, with `192x208` cells.
- PNG or WebP with a real alpha channel.
- Each upload sheet is at most 12 MiB; final atlas is at most 4 MiB.
- Standardized delivery must pass `--strict --frame-counts frame-counts.json`.
- Keep at least 8 px of transparent margin inside each cell; reject crossed edges, clipped content, whole blank actions, internal empty slots or counts differing from the approved plan.
- Inspect both cut-line overlays at fixed 192 px / 208 px intervals: each populated cell contains exactly one complete pose and its own props, without neighboring fragments. Overlays are review-only.
- Confirm the atlas pixels match the two delivery sheets.
- Fully transparent cells remain in position and do not shift later frames.

## Identity

- Same body type, face, silhouette, proportions, palette, materials, markings, clothing, lighting language, and persistent props across every row.
- No row introduces an unintended character, scene, or inconsistent object.
- Details remain readable at `192x208`.

## Animation

- Every row communicates the state described in `animation-rows.md`.
- First and last meaningful frames form a reasonable loop.
- `running-right` faces right and `running-left` faces left with alternating cadence.
- Scale, center, and baseline do not pop between frames unless motivated by the action. Use one row-wide scale and reviewed anchors; preserve airborne motion rather than automatically grounding every frame.
- `grabbed` reads as externally suspended or dragged without depicting UI or a cursor.
- Repeated frames are intentional; accidental identical or missing poses should be repaired.

## Clean output

- Real transparency, without white, black, checkerboard, or chroma background residue.
- No grid, border, label, number, action name, explanation, watermark, UI, or scene background.
- No detached stars, punctuation, icons, speed lines, dust, floor shadows, glow, aura, motion trails, or fragments in neighboring cells.
- Effects needed for `success` or `failed` remain attached to the character, opaque enough for clean extraction, and inside the same cell.

## Repair order

1. Correct extraction, centering, or transparency without regenerating art when the source row is sound.
2. In Mixed or Precision mode, repair or regenerate one bad row and replace only that row.
3. In Fast mode, regenerate the affected whole sheet or explicitly switch the failed rows to Mixed-mode repair.
4. Regenerate the canonical character only when identity is broadly wrong.
5. Rebuild the atlas and repeat previews after the smallest necessary repair.

