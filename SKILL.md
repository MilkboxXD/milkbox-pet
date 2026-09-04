---
name: milkbox-pet
description: Design, discuss, approve, then create, repair, validate, and package MilkboxViewer resident characters from text or reference art. Use for concept-first resident design and, only after explicit visual approval, the MilkboxViewer two-sheet 8x6 delivery format or final pet-v2 8x12 atlas; do not use for the Codex 8x9 pet format.
---

# Milkbox Pet

Create a consistent animated resident character for MilkboxViewer while preserving the image-generation, deterministic assembly, and visual-QA principles of the official `hatch-pet` workflow.

Read [references/milkboxviewer-contract.md](references/milkboxviewer-contract.md) before producing, repairing, validating, or packaging images. Read [references/animation-rows.md](references/animation-rows.md) before writing row prompts. Use [references/qa-rubric.md](references/qa-rubric.md) for final review.

## Required approval gates

This is a concept-first workflow. Invoking this skill is not permission to start image generation or animation production immediately.

### Gate 1: collect the character direction

If the user has not supplied either a concrete character description or a reference image, stop and ask what kind of resident they want or invite them to attach reference art. Do not call `$imagegen`, create production folders, select a species or object, invent a palette, infer a mascot from the project/folder name, or begin the animation checklist.

For a broad request such as “use this skill to generate a resident image,” ask one compact question covering the minimum useful choices:

- character form or species, such as person, animal, object mascot, robot, or fantasy creature
- desired visual style, such as pixel, sticker, plush, clay, flat vector, or 3D toy
- signature colors, clothing, markings, or props
- alternatively, ask the user to upload a reference image

Offer a few examples when helpful, but do not choose an example for the user. Continue only after the user provides enough direction or a reference image.

### Gate 2: create and discuss one concept image

After Gate 1 has enough input, generate only one canonical full-body concept image. This is a discussion draft, not an animation row or delivery spritesheet.

Show the concept image to the user and ask whether its form, proportions, face, palette, clothing, markings, props, and style should be changed. Iteratively edit or regenerate only the canonical concept while the user is discussing it.

Do not generate action rows, derive `running-left`, compose sheets, render animation previews, or run final delivery packaging during concept discussion. Feedback such as “cute,” “looks good,” or requested concept edits does not by itself authorize animation production.

### Gate 3: explicit animation approval

Begin the twelve-action animation workflow only after the user clearly approves the current concept and explicitly asks to proceed with animation, for example:

- “確認這個造型，開始做動畫。”
- “這版可以，請產生 12 個動作。”
- “用這張定稿製作 MilkboxViewer 圖集。”

If approval or animation intent is ambiguous, ask for confirmation and do not generate animation images yet. A user who supplies an already-approved canonical character and explicitly requests the twelve actions may enter Gate 3 directly.

After animation approval, ask the user to choose a production mode unless they already selected one:

- **Mixed (recommended):** generate two source images, each containing six horizontal animation sequences, run deterministic and visual QA, then regenerate and replace only failing action sequences.
- **Fast:** generate the same two source images and accept or regenerate at whole-image scope. Use when minimizing generation count matters more than fine repair control.
- **Precision:** generate twelve separate horizontal animation sequences and compose them deterministically. Use when action fidelity and the smallest possible repair scope matter more than generation count.

Explain the tradeoff in one short sentence. If the user asks the skill to decide, use Mixed. Do not begin visual generation while waiting for this choice.

Treat each gate as a stopping condition. Finish the current gate, return its result or question, and wait for the user's next message instead of continuing automatically into the next gate.

## Image generation

Use `$imagegen` for normal visual generation and editing. Load its `SKILL.md` before generating images. Scripts in this skill may only perform deterministic layout, transparency cleanup, resizing, preview rendering, and validation; they must not invent missing character artwork.

If the user provides reference art, treat it as the identity source of truth. Otherwise generate one centered full-body canonical character only after Gate 1 is satisfied. Lock the approved species/body type, face, silhouette, proportions, palette, material, line treatment, lighting, markings, clothing, and persistent props across all rows.

Keep file-format language separate from image-generation language. The delivery contract is technically an 8-column × 6-row sheet, but do not prompt the image model with only “8×6 grid”, “spritesheet grid”, or an equivalent bare grid instruction. Models may treat that as a static contact sheet instead of animation.

In Fast or Mixed mode, generate two complete images from the approved canonical character. Describe each image as six stacked horizontal animation sequences in the fixed action order. Each sequence shows one continuous action progressing from left to right in no more than eight successive frames. Ask for consistent spacing, scale, center, and baseline; unused trailing frame positions remain fully transparent. Sheet 1 contains actions 1–6 and sheet 2 contains actions 7–12. Image tools may require one generation call per sheet; do not claim that both images came from a single call when they did not.

In Precision mode, or when Mixed-mode QA identifies a failing action, prompt for one horizontal continuous animation sequence for the required action. The motion progresses from left to right in up to eight successive frames; if fewer frames communicate the motion, leave the unused trailing frame positions fully transparent. Do not ask the model merely for an “eight-slot strip.” Attach the approved canonical character and the relevant layout guide or prior approved output whenever the image tool supports references.

Prefer transparent output. A flat chroma background may be used only when it can be removed cleanly without deleting character colors.

Each action always reserves eight frame positions in the delivery file. The generated motion may use at most eight frames. When fewer frames are sufficient, leave the unused trailing positions fully transparent; repeat a frame only when timing needs an intentional hold. Never collapse the sequence or shift later actions into its unused positions.

`running-right` may be mirrored frame-by-frame to derive `running-left` only when asymmetrical markings, text, lighting, clothing, props, and handedness remain correct. Preserve temporal frame order; do not mirror the whole strip in a way that reverses cadence.

## Fixed row order

Sheet 1 contains rows 1–6:

1. `idle`
2. `running-right`
3. `running-left`
4. `waving`
5. `reading-writing`
6. `rubbing`

Sheet 2 contains rows 7–12:

1. `washing`
2. `examining`
3. `resting`
4. `success`
5. `failed`
6. `grabbed`

Do not add, delete, reorder, rename, or substitute rows.

## Animation production workflow

Create this production checklist only after Gate 3 is satisfied:

1. Lock the explicitly approved canonical character as the identity reference.
2. Record the selected production mode.
3. Generate the initial sheets or rows for that mode.
4. Standardize and validate the delivery, render motion previews, and visually inspect every state.
5. In Mixed mode, regenerate only failing states and replace their rows; then rebuild and recheck the atlas.

### Mixed and Fast mode

Generate the two source images as six stacked, left-to-right animation sequences per image. Do not use the bare technical phrase “8×6 grid” as the image prompt. After generation, interpret the reserved frame positions as the technical 8×6 delivery layout, standardize them, and create the atlas:

```powershell
python scripts/standardize_sheets.py --sheet1 <generated-sheet-1> --sheet2 <generated-sheet-2> --output-dir <delivery-directory>
```

Render previews and inspect all twelve action semantics. Deterministic validation cannot detect a semantically wrong pose, identity drift, or incorrect row order by itself, so visual QA is mandatory.

In Mixed mode, for each failing state generate one corrected horizontal continuous animation sequence of up to eight frames, with unused trailing positions transparent, and replace it in the relevant standardized sheet:

```powershell
python scripts/replace_sheet_row.py --sheet <current-sheet> --sheet-number <1-or-2> --state <state> --replacement <corrected-row> --output <repaired-sheet>
```

Use the state contract to select the expected sheet and row; the script rejects a mismatched `--sheet-number`. After all replacements, run `standardize_sheets.py` again with the repaired pair to rebuild the final atlas, followed by validation and preview generation. Stop repairing when every deterministic check passes and visual QA accepts every row. Do not regenerate an accepted row merely for stylistic variety.

Fast mode does not automatically create row repairs. If QA fails, tell the user which rows failed and ask whether to regenerate the affected whole sheet or switch those rows to Mixed-mode repair.

### Precision mode

Compose approved row strips with:

```powershell
python scripts/compose_from_rows.py --rows-dir <rows-directory> --output-dir <delivery-directory>
```

The rows directory must contain `<state>.png` or `<state>.webp` for all twelve state names. Each source is interpreted as eight equal horizontal slots. The composer normalizes every slot into `192x208`, preserves aspect ratio, centers the visible content, and writes:

```text
delivery/
  milkbox-pet-sheet-1.png
  milkbox-pet-sheet-2.png
  milkbox-pet-v2-atlas.png
```

If generated rows use a flat chroma key, pass `--chroma-key RRGGBB` and an appropriate `--chroma-tolerance`; inspect edges visually afterward.

Validate delivery images with:

```powershell
python scripts/validate_pet_images.py --sheet1 <sheet-1> --sheet2 <sheet-2> --atlas <atlas> --json-out <validation.json>
```

Render per-action GIF previews with:

```powershell
python scripts/render_previews.py --sheet1 <sheet-1> --sheet2 <sheet-2> --output-dir <preview-directory>
```

Input sheets are allowed to differ from `1536x1248` because MilkboxViewer provides adjustable cut lines. Treat nonstandard dimensions as a warning, not an automatic failure, as long as the 8×6 layout remains clear. Images produced by this skill should target the exact standard size whenever deterministic composition is available.

## Visual constraints

- Transparent background with genuine alpha; no white or checkerboard substitute.
- No visible grids, borders, labels, row numbers, action names, explanatory text, watermarks, UI, or scene background in delivery files.
- Keep every visible pixel within its own cell. Reject clipping, cross-cell overlap, neighboring fragments, or detached effects.
- Keep character scale, visual center, and baseline stable unless the action intentionally changes them.
- Prefer pose, expression, and silhouette changes over motion lines, dust, glows, floor shadows, floating icons, or other detached effects.
- Accept pixel, plush, clay, sticker, vector, 3D-toy, painterly, ink, or other styles when the character remains readable inside `192x208` and consistent across all rows.

## Repair and acceptance

Repair one frame or one row before regenerating both sheets. Regenerate the canonical character only when identity is broadly wrong.

Do not accept the delivery until deterministic validation passes and the two sheets plus motion previews pass the visual rubric. The required final atlas is `1536x2496`, 8 columns × 12 rows, with `192x208` cells and a maximum size of 4 MiB. Each original upload sheet must be PNG or WebP and no larger than 12 MiB.
