---
name: milkbox-pet
description: "Create, repair, and validate MilkboxViewer resident artwork through character approval, twelve-action planning, image generation, deterministic frame alignment, visual QA, and two-sheet 8x6 / pet-v2 8x12 delivery. Use for MilkboxViewer residents, not the Codex 8x9 pet format."
---

# Milkbox Pet

Create a consistent animated resident character for MilkboxViewer while preserving the image-generation, deterministic assembly, and visual-QA principles of the official `hatch-pet` workflow.

Read [references/milkboxviewer-contract.md](references/milkboxviewer-contract.md) before producing, repairing, validating, or packaging images. Read [references/animation-rows.md](references/animation-rows.md) before discussing or writing animation-row prompts. Read [references/frame-alignment.md](references/frame-alignment.md) before production or alignment repair. Use [references/qa-rubric.md](references/qa-rubric.md) for final review.

## Mandatory user-visible workflow

This skill is a strict, concept-first, user-visible staged workflow. Invoking the skill is not permission to start image generation or animation production immediately.

For every new Milkbox Pet production request, first show the user the workflow and the final acceptance criteria. Do not silently advance through stages.

The normal sequence is:

1. **Workflow declaration and acceptance criteria**
2. **Character direction**
3. **Canonical concept image**
4. **Character approval**
5. **Animation action discussion**
6. **Animation-plan approval and production mode**
7. **Production**
8. **QA, repair, and delivery**

At every stage transition, explicitly tell the user:

- which stage has just been completed
- which stage is starting now
- what will be decided, reviewed, or produced in that stage

Keep stage announcements concise. Do not repeatedly print the entire workflow unless the user asks.

A stage may be skipped only when the user explicitly provides the result of that stage and clearly states that it is already approved. Never treat possessing enough information as equivalent to user approval.

Information availability and user approval are separate conditions.

When a stage requires approval, finish the current stage, present the result or choices, and wait for the user's next message. Do not silently cross an approval gate.

## Stage 1: workflow declaration and acceptance criteria

Every new character-production run must begin here, even when the user already supplied a complete character description or reference image.

Before character design or image generation, briefly tell the user that the work will proceed through the eight stages listed above and that approval stages are stopping points.

Then show the delivery acceptance criteria.

At minimum, state all of the following:

- Deliver **2 character sheets**.
- Each sheet uses an **8-column × 6-row** layout.
- Each sheet contains **48 reserved cells**.
- Each row represents exactly **1 action**.
- Each action may use up to **8 successive frames from left to right**.
- Preferred sheet size: **1536 × 1248 px**.
- Standard cell size: **192 × 208 px**.
- Delivery format: **PNG or WebP**.
- Background must contain **genuine transparency**.
- No visible grid lines, borders, labels, action names, frame numbers, UI, scenery, watermarks, or explanatory text.
- Character identity, proportions, palette, clothing, markings, and persistent props must remain consistent.
- Visible pixels must remain inside their own reserved cells with at least 8 px of transparent padding in standardized delivery files.
- Both sheets must support the same fixed straight cuts every 192 px horizontally and 208 px vertically; inspect separate cut-line overlays before acceptance.
- Sheet 1 contains actions 1–6.
- Sheet 2 contains actions 7–12.
- Final standardized atlas is **1536 × 2496 px**, 8 columns × 12 rows.
- Final atlas must be **no larger than 4 MiB**.
- Each original uploaded sheet must be PNG or WebP and **no larger than 12 MiB**.
- Deterministic validation and visual QA must both pass before final acceptance.

Also show the fixed action order:

**Sheet 1**

1. `idle`
2. `running-right`
3. `running-left`
4. `waving`
5. `reading-writing`
6. `rubbing`

**Sheet 2**

7. `washing`
8. `examining`
9. `resting`
10. `success`
11. `failed`
12. `grabbed`

After presenting the workflow and acceptance criteria, explicitly announce that the next stage is **Stage 2: Character direction**.

Stage 1 itself is not an approval gate unless the user questions or changes the acceptance criteria. Its purpose is to establish a shared workflow and definition of done.

If the user already supplied a character description or reference image in the same request, Stage 1 may immediately transition into Stage 2 and summarize that input in the same response. Stage 1 itself must never be omitted.

During Stage 1:

- do not generate a concept image
- do not discuss detailed animation poses
- do not ask for production mode
- do not begin animation production

## Stage 2: character direction

Goal: establish exactly what the resident should look like.

Collect or confirm:

- character form or species, such as person, animal, object mascot, robot, or fantasy creature
- desired visual style, such as pixel, sticker, plush, clay, flat vector, 3D toy, painterly, or another user-specified style
- signature colors
- clothing
- markings
- persistent props
- reference image, if any

If the user has not supplied either a concrete character description or a reference image, stop and ask one compact question covering the minimum useful choices or invite them to attach reference art.

Do not call `$imagegen`, create production folders, select a species, invent a palette, infer a mascot from the repository/project name, or begin animation planning while the character direction is still missing.

If enough information already exists, briefly summarize the interpreted character direction so the user can see what will be used.

Exit condition: a sufficiently concrete character direction exists.

Then announce **Stage 3: Canonical concept image**.

## Stage 3: canonical concept image

Goal: create exactly one canonical full-body character concept for discussion.

After Stage 2 has enough input, generate only one centered, full-body canonical concept image. This is a discussion draft, not an animation row or delivery spritesheet.

If the user provides reference art, treat it as the identity source of truth.

Show the concept image to the user and ask whether its form, proportions, face, palette, clothing, markings, props, and style should be changed.

Iteratively edit or regenerate only the canonical concept while the user is discussing it.

Do not generate action rows, derive `running-left`, compose sheets, render animation previews, or run final delivery packaging during concept discussion.

Feedback such as “cute,” “looks good,” or a requested edit does not by itself authorize animation production.

Exit condition: the current concept image exists and has been shown for review.

Stop and wait for the user's explicit character approval or revision request.

## Stage 4: character approval

Goal: lock the canonical visual identity.

The user must explicitly approve the current concept before animation planning can be finalized.

Examples of sufficient approval:

- “確認這個造型。”
- “這個角色定稿。”
- “就用這張。”
- “確認這個造型，開始做動畫。”

Do not interpret vague positive feedback such as “可愛”, “不錯”, or “好多了” as final approval unless the intent is clearly to lock the design.

Once approved, lock the species/body type, face, silhouette, proportions, palette, material, line treatment, lighting, markings, clothing, and persistent props as the canonical identity reference.

Character approval authorizes **animation planning**, not animation image generation.

After approval, explicitly announce:

> 下一階段：**Stage 5 / 8 動作細節討論**。這一階段只確認 12 個動作怎麼演、需要幾格與角色專屬細節，不生成正式動畫圖。

## Stage 5: animation action discussion

Goal: discuss how the approved character performs all twelve MilkboxViewer actions before generating production animation artwork.

Read [references/animation-rows.md](references/animation-rows.md) before proposing the action plan.

Present all twelve actions in the fixed row order and translate the generic action definitions into character-specific motion ideas.

For every action, discuss or propose:

- action semantics
- starting pose
- main motion
- ending or loop pose
- approximate useful frame count, up to 8
- character-specific expression or personality
- persistent-prop behavior
- any special constraint, such as whether mirroring is unsafe

The fixed actions remain:

1. `idle`
2. `running-right`
3. `running-left`
4. `waving`
5. `reading-writing`
6. `rubbing`
7. `washing`
8. `examining`
9. `resting`
10. `success`
11. `failed`
12. `grabbed`

Do not add, delete, reorder, rename, or substitute states.

The user may change how an action is visually performed as long as its semantic meaning remains valid.

Do not generate production animation images during this stage, including “preview” rows or trial spritesheets.

After presenting the complete action plan, explicitly state that it is still a motion-design proposal and ask for revisions or approval.

Exit condition: the user has reviewed the twelve-action plan.

Stop and wait for explicit approval or requested changes.

## Stage 6: animation-plan approval and production mode

Goal: lock the twelve-action motion design and decide how it will be produced.

Begin production only after the user explicitly approves the action plan, for example:

- “動作就照這版。”
- “確認動作，開始製作。”
- “這 12 個動作可以，開始生成。”

If approval is ambiguous, ask for confirmation and do not generate animation images.

After action-plan approval, ask the user to choose a production mode unless they already selected one:

- **Mixed (recommended):** generate two source images, each containing six horizontal animation sequences, run deterministic and visual QA, then regenerate and replace only failing action sequences.
- **Fast:** generate the same two source images and accept or regenerate at whole-image scope. Use when minimizing generation count matters more than fine repair control.
- **Precision:** generate twelve separate horizontal animation sequences and compose them deterministically. Use when action fidelity and the smallest possible repair scope matter more than generation count.

Explain the tradeoff in one short sentence. If the user asks the skill to decide, use Mixed.

Do not begin visual generation while waiting for the mode selection.

Record the approved useful frame count for each state in `frame-counts.json`; counts include intentional holds and exclude unused trailing cells.

Exit condition: both the twelve-action plan and production mode are confirmed.

Only now may animation production begin.

## Production entry invariant

Animation production is forbidden unless all of the following are true:

- Stage 1 workflow and acceptance criteria were shown to the user
- canonical character direction exists
- canonical concept image exists
- canonical character has explicit user approval
- all twelve actions have been discussed
- twelve-action motion plan has explicit user approval
- production mode has been selected

If any item is missing, return to the corresponding stage.

Having enough information to infer a missing decision does not satisfy this requirement.

Never generate animation artwork “for preview” before Stage 6 is complete.

## Image generation

Use `$imagegen` for normal visual generation and editing. Load its `SKILL.md` before generating images. Scripts in this skill may only perform deterministic layout, transparency cleanup, resizing, preview rendering, compression, and validation; they must not invent missing character artwork.

Keep file-format language separate from image-generation language. The delivery contract is technically an 8-column × 6-row sheet, but do not prompt the image model with only “8×6 grid”, “spritesheet grid”, or an equivalent bare grid instruction. Models may treat that as a static contact sheet instead of animation.

In Fast or Mixed mode, generate two complete images from the approved canonical character and approved action plan. Describe each image as six stacked horizontal animation sequences in the fixed action order. Each sequence shows one continuous action progressing from left to right in no more than eight successive frames. Ask for consistent spacing, scale, center, and baseline; unused trailing frame positions remain fully transparent. Sheet 1 contains actions 1–6 and Sheet 2 contains actions 7–12. Image tools may require one generation call per sheet; do not claim that both images came from a single call when they did not.

In Precision mode, or when Mixed-mode QA identifies a failing action, prompt for one horizontal continuous animation sequence for the required action. The motion progresses from left to right in up to eight successive frames; if fewer frames communicate the motion, leave unused trailing frame positions fully transparent. Do not ask the model merely for an “eight-slot strip.” Attach the approved canonical character and the relevant layout guide or prior approved output whenever the image tool supports references.

Request the same eight reserved horizontal positions across every row, with complete poses and transparent gutters. Six-frame actions use only positions 1–6, leaving 7–8 transparent; never distribute fewer frames across the whole row. Do not draw positioning guides.

Prefer transparent output. A flat chroma background may be used only when it can be removed cleanly without deleting character colors.

Each action always reserves eight frame positions in the delivery file. The generated motion may use at most eight frames. When fewer frames are sufficient, leave unused trailing positions fully transparent; repeat a frame only when timing needs an intentional hold. Never collapse the sequence or shift later actions into unused positions.

`running-right` may be mirrored frame-by-frame to derive `running-left` only when asymmetrical markings, readable text, lighting, clothing, props, and handedness remain correct. Preserve temporal frame order; do not mirror the whole strip in a way that reverses cadence.

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

## Stage 7: production

Create this production checklist only after Stage 6 is fully satisfied:

1. Lock the explicitly approved canonical character as the identity reference.
2. Lock the explicitly approved twelve-action plan.
3. Record the selected production mode.
4. Generate the initial sheets or rows for that mode.
5. Extract complete frames from reviewed source rows, register them with a common row scale, and pack fixed cells as described in `references/frame-alignment.md`. Generated artwork is not a delivery sheet.
6. Compose the normalized rows and build the atlas.
7. Proceed to Stage 8 for validation and visual QA, including cut-line overlays.

### Mixed and Fast mode

Generate the two source images as six stacked, left-to-right animation sequences per image. Do not use the bare technical phrase “8×6 grid” as the image prompt.

After generation, inspect the actual row boundaries and prepare `extraction.json` using [references/frame-alignment.md](references/frame-alignment.md). Extract each row's approved number of complete frames, then deterministically pack fixed cells:

```powershell
python scripts/normalize_generated_rows.py --manifest extraction.json --output-dir normalized-rows
python scripts/compose_from_rows.py --rows-dir normalized-rows --output-dir delivery
```

Never pass unaligned source artwork directly to an equal-grid slicer. If extraction cannot separate complete poses without cutting visible pixels, repair/regenerate the failed row under the selected mode's existing repair policy. Do not silently drop pixels or change approved frame counts.

### Precision mode

Normalize the generated strips before composition:

```powershell
python scripts/normalize_generated_rows.py --input-dir source-rows --frame-counts frame-counts.json --output-dir normalized-rows
python scripts/compose_from_rows.py --rows-dir normalized-rows --output-dir delivery
```

Use the manifest route when explicit cuts or registration anchors are needed. The normalized directory must contain `<state>.png` or `<state>.webp` for all twelve states, each exactly `1536x208`. The composer preserves these registered frames and writes:

```text
delivery/
  milkbox-pet-sheet-1.png
  milkbox-pet-sheet-2.png
  milkbox-pet-v2-atlas.png
```

All production modes must use a common scale within each action, keep 8 px transparent cell margins, and preserve approved intentional movement through registration anchors. Do not independently enlarge each pose to fill its cell. See the alignment reference for original alpha/chroma handling and manifest coordinates.

## Stage 8: QA, repair, and delivery

Validate delivery images with:

```powershell
python scripts/validate_pet_images.py --sheet1 <sheet-1> --sheet2 <sheet-2> --atlas <atlas> --strict --frame-counts frame-counts.json --json-out <validation.json>
```

Render per-action GIF previews with:

```powershell
python scripts/render_previews.py --sheet1 <sheet-1> --sheet2 <sheet-2> --output-dir <preview-directory>
```

The preview command also writes separate `sheet-1-cut-overlay.png` and `sheet-2-cut-overlay.png` QA images. Inspect every cell against the fixed cut lines and 8 px margins; never deliver these overlays as spritesheets.

Render previews and inspect all twelve action semantics. Deterministic validation cannot detect a semantically wrong pose, identity drift, incorrect action meaning, or incorrect row order by itself, so visual QA is mandatory.

In Mixed mode, for each failing state generate one corrected horizontal continuous animation sequence of up to eight frames, with unused trailing positions transparent, normalize it using the alignment workflow, and replace the normalized row in the relevant standardized sheet:

```powershell
python scripts/replace_sheet_row.py --sheet <current-sheet> --sheet-number <1-or-2> --state <state> --replacement <normalized-corrected-row> --output <repaired-sheet>
```

Use the state contract to select the expected sheet and row; the script rejects a mismatched `--sheet-number`.

After all replacements, run `standardize_sheets.py` on the already aligned sheets with the repaired pair to rebuild the final atlas, followed by validation and preview generation.

Stop repairing when every deterministic check passes and visual QA accepts every row. Do not regenerate an accepted row merely for stylistic variety.

Fast mode does not automatically create row repairs. If QA fails, tell the user which rows failed and ask whether to regenerate the affected whole sheet or switch those rows to Mixed-mode repair.

Repair one frame or one row before regenerating both sheets. Regenerate the canonical character only when identity is broadly wrong.

If the standardized final atlas exceeds 4 MiB, compress or optimize it without changing atlas geometry, alpha transparency, row order, cell boundaries, or visible character fidelity, then validate it again.

Input sheets are allowed to differ from `1536x1248` because MilkboxViewer provides adjustable cut lines. Treat nonstandard dimensions as a warning, not an automatic failure, as long as the 8×6 layout remains clear. Images produced by this skill must be deterministically composed at the exact standard size and pass `--strict` validation. The source-upload warning policy never relaxes final acceptance.

## Visual constraints

- Transparent background with genuine alpha; no white or checkerboard substitute.
- No visible grids, borders, labels, row numbers, action names, explanatory text, watermarks, UI, or scene background in delivery files.
- Keep every visible pixel within its own cell. Reject clipping, cross-cell overlap, neighboring fragments, or detached effects.
- Keep character scale, visual center, and baseline stable unless the approved action intentionally changes them.
- Preserve the approved character identity across every row.
- Prefer pose, expression, and silhouette changes over motion lines, dust, glows, floor shadows, floating icons, or other detached effects.
- Accept pixel, plush, clay, sticker, vector, 3D-toy, painterly, ink, or other styles when the character remains readable inside `192x208` and consistent across all rows.

## Final acceptance

Do not accept the delivery until deterministic validation passes and the two sheets plus motion previews pass the visual rubric.

The required final atlas is:

- `1536x2496`
- 8 columns × 12 rows
- `192x208` cells
- genuine alpha transparency
- maximum size **4 MiB**

Each original upload sheet must be PNG or WebP and no larger than **12 MiB**.

When Stage 8 succeeds, explicitly tell the user that QA has passed and the workflow is complete.
