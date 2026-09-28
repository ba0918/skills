---
name: ba0918-codex-image
description: "Make image assets for games and websites with the Codex CLI's image generation (codex exec), keeping a consistent look through a series — a reference image plus a style definition kept in a project folder. It turns a rough request into a prompt, generates, then runs a bundled script for fixed post-processing (pixel-sprite dot grids, sizes, transparency, animation sheets, GIF previews) and automatic acceptance checks with up to two automatic retries, and stores the result in the series folder. Runs only when the user names this skill or asks for image generation with Codex; images merely coming up in conversation is not a request. The prompt, the reference image, and the template image are sent to the model provider (OpenAI) without asking again; project files are not placed where Codex runs. Use when the user says make this asset with codex-image, generate a sprite with Codex, or make an animation sheet with Codex. 日本語キーワード: codex-image Codex で画像生成 Codex で素材を作って ドット絵 立ち絵 アニメーション スプライトシート Web 素材 シリーズ"
---

# Codex Image Assets

## Scope

This skill makes image assets — pixel sprites, illustrations, web images, and animation sheets —
with the image generation built into the Codex CLI, and keeps their look consistent. Generation
is Codex's job. This skill owns everything around it: the series (the reference image and the
style definition), turning a rough request into a prompt, fixed post-processing, automatic
acceptance checks, and where the files end up.

Terms used throughout:

- **Series** — a group of assets that should share one look. It has a reference image
  (`reference.png`) and a style definition (`series.md`), kept in a project folder the user
  chooses. Do not call it a "set" or a "theme".
- **Pixel sprite** — an image whose every dot sits on an exact grid (for example 32×32 dots, each
  one colour). `kind: pixel`. Only pixel sprites get the dot-grid post-processing and the dot-size
  check.
- **Pixel-style illustration** — a high-resolution picture that only looks like dot art and does
  not sit on a grid. It is handled as an illustration (`kind: illustration`).
- **Template image** — the image attached when generating an animation sheet: an empty sheet with
  the character's stand image in the top-left cell only. The subcommand that makes it is named
  `template`; the image itself is always called the template image.

Never say "pixel art": it reads as either of the two kinds above.

Not covered: video, audio, vector images, editing existing images that belong to no series,
generating many assets in one batch, being started automatically by another workflow, and
non-square pixel-sprite canvases.

## When this runs

Run only when the user names this skill or asks for image generation with Codex — for example
"codex-image: a bat stand image" or "make the assets with Codex". An image merely coming up in
conversation ("this page needs a hero image") or a question about image generation is not a
request: answer it, and do not start `codex exec`.

## What is sent

Each generation sends the prompt and one attached image — the reference image or the template
image — to the model provider, OpenAI. Being named counts as the decision to send them: do not
ask for confirmation again before generating.

Project files are never placed where Codex runs. Codex runs in a temporary working folder that
holds only the prompt and the one image. The sandbox allows writing only inside that folder, but
it does not restrict reading, so this keeps project files out of what is sent without
guaranteeing that Codex never reads outside the folder. Say so if the user asks.

## Before generating

Check these before anything is generated, and stop without generating when one fails, telling
the user exactly what is missing:

1. `codex --version` succeeds.
2. `codex features list` shows `image_generation` as enabled.
3. The post-processing script actually starts: `uv run --with pillow scripts/codex_image.py
   --help` succeeds, or, when Pillow is installed, `python3 scripts/codex_image.py --help` does.
   The script loads Pillow before printing its help, so this also catches Pillow failing to
   install. Run every later step of the script the same way as the command that succeeded.
4. For an animation: the series is `kind: pixel` with `transparent: true`, and the character's
   stand image `<character>/final.png` exists in the series folder (see Animation).

Checking the post-processing first matters: finding out afterwards would throw away a paid
generation.

## The post-processing script

`scripts/codex_image.py` in this skill's directory does every step whose result must be exact.
Never do these steps by hand or with ad-hoc code. Run it with `uv run --with pillow
scripts/codex_image.py ...` (use the script's full path when running from elsewhere), or with
`python3` when Pillow is installed.

```
codex_image.py template --stand <PNG> [--frames <F>] --out <PNG>
codex_image.py process  --series <series.md> --raw <PNG> --out <PNG> [--frames <F> --stand <PNG>] [--no-ground]
codex_image.py check    --series <series.md> --raw <PNG> [--frames <F> --stand <PNG>] [--no-ground]
codex_image.py preview  --sheet <PNG> --frames <F> --out <GIF> [--ms <N>]
```

- `template` without `--frames` enlarges a pixel sprite to 10 px per dot with nearest-neighbour
  scaling; use it to attach a pixel sprite reference. With `--frames` it makes the template
  image. The canvas size in dots is read from the stand image, which must be square.
- `process` turns the raw image into the finished asset. Without `--frames` it handles one asset;
  with `--frames` (2 to 16, needs `--stand`) it handles an animation sheet. `--no-ground` keeps
  frames at their drawn height instead of aligning the feet.
- `check` judges the raw image without changing it and prints
  `{"result": "pass" | "fail" | "undetermined", "reasons": [...], "measures": {...}}`, exiting 0
  for all three. `measures` is printed whatever the result. For a pixel sprite it holds
  `dot_size_x` and `dot_size_y`, the estimated size of one dot in px (`null` when it cannot be
  estimated); for an animation it also holds `top_left_diff`, the share of the top-left cell's
  dots that differ from the stand image. Illustrations and web images measure nothing, so their
  `measures` is empty.
- Any subcommand exits non-zero with the reason on standard error when an input is wrong — for
  example a `series.md` with a missing or malformed field. `process` also exits non-zero, writing
  nothing, when aligning the feet would push a frame above the top of its cell.

What `process` does, by kind:

| Kind | Post-processing |
|---|---|
| Pixel sprite | Takes the colour at the centre of each dot's cell. Keeps every colour. With `transparent: true`, alpha 128 and above becomes opaque and the rest fully transparent; with `false` the background stays |
| Illustration (including pixel-style) | `transparent: true`: scaled to fit inside `size`, the rest filled with transparency, soft edges kept. `false`: cropped from the centre to the ratio of `size`, then scaled to `size` |
| Web image | Always opaque. Cropped from the centre to the ratio of `size`, then scaled to `size` |

## Series

The series folder is a folder in the project that the user chooses:

```
<series folder>/
  series.md          the series definition
  reference.png      the reference image
  <asset>/           one folder per asset (an animation uses <character>-<motion>/)
    final.png        the finished asset (a sheet for an animation)
    raw.png          the unprocessed image Codex produced
    prompt.md        the prompt used, plus the user's feedback appended
    preview.gif      animation preview (animations only)
```

`series.md` starts with a front matter block that the script reads. Write each value exactly in
the form shown — no quotes, no comments on the line, no nesting:

```
---
kind: pixel
canvas_dots: 32
transparent: true
---
```

| Field | Value | Used by |
|---|---|---|
| `kind` | `pixel`, `illustration`, or `web` | all |
| `canvas_dots` | dots along one side of the square canvas, such as `32` | `pixel` |
| `size` | output `WIDTHxHEIGHT` in pixels, such as `1024x1024` | `illustration`, `web` |
| `transparent` | `true` or `false`; there is no default, so a kind that uses it must state it | `pixel`, `illustration` |

The body, in prose, says what later assets carry over from the reference (the drawing style,
palette, line work, shading) and what they do not (shapes, faces, poses, subjects), plus any other
notes on the look. For a pixel-style illustration series, say in the body that it is a
pixel-style illustration handled as an illustration.

A pixel-sprite `reference.png` is the processed, finished sprite at its real size (for example
32×32). Enlarge it with `template` (without `--frames`) only when attaching it to a generation.

### Starting a new series

When the series has no reference image yet:

1. Ask, in one message, for what cannot be derived: the kind, the first size or canvas, whether
   the background is transparent, and what the assets are for.
2. Write the front matter those answers give to a temporary `series.md` outside the project, so
   the candidates can be processed and checked.
3. Generate three candidates from the style description alone, each varying the direction a
   little (colour, proportions, and so on), without an attached image. Run `process` and `check`
   on each. Do not retry candidates automatically; attach the reasons to any that failed.
4. Show the three processed candidates and let the user choose one. Never choose for them.
5. Save the chosen processed image as `reference.png` in the series folder, and write
   `series.md` there, with the front matter and a body describing what to carry over and what
   not.

After that, assets are made one at a time with the reference. Make several candidates only when
the user asks.

## Turning a rough request into a prompt

The user asks roughly; build the prompt yourself from `references/prompts.md`. Read it every time
you build a prompt.

- Fill in from the series whatever it defines: the kind, the size, the dot count, the look. Do not
  ask about these.
- Ask only what cannot be filled in — which series is meant, when that is unclear, or the first
  size and purpose of a new series — all together, before generating.
- Do not show the prompt for approval. Generate right away and keep the prompt in `prompt.md`.
- When a reference image is attached, the prompt states separately what to carry over and what
  not to carry over; otherwise Codex copies eyes and shapes from the reference.
- Every prompt tells Codex to save the generated image unchanged, without scaling, cropping, or
  editing it, as `raw.png` in the working folder. Without this Codex post-processes the image in
  a different way every time.
- A web-image prompt asks for the ratio of `size` and keeps the subject out of the outer tenth
  of each edge.
- Name the asset with a short English name derived from the request (`bat`, `bat-attack`,
  `top-hero`), unless the user gave one, and say the name when generation starts. If a folder
  with that name already exists, ask whether to overwrite it as a remake before going on.

## Animation

One sheet holds one motion. Frames: 2 to 16, 8 by default. The sheet is always 4 columns wide,
with as many rows as the frame count divided by 4, rounded up (4 frames: 1×4, 8: 2×4, 12: 3×4,
16: 4×4). Unused cells stay transparent. The fixed column count makes cutting frames out of the
sheet easy on the game side.

- Only `kind: pixel` series with `transparent: true` can have animations. For any other series,
  generate nothing and say that animations cannot be made for a series with a background: finding
  the feet at the lowest opaque dot and leaving unused cells transparent both need transparency.
- The top-left cell of the template image holds the character's adopted stand image,
  `<character>/final.png`. When the character has no stand image, generate nothing and say to
  make the stand image first.
- Make the template image with `template --stand <character>/final.png --frames <F>` and attach
  it.
- The prompt tells Codex not to draw effect frames such as white flashes or fades. Draw them only
  when the user explicitly asks.
- `process` puts the original stand image back in the top-left cell and aligns every frame's
  feet with its feet, never moving frames sideways. For a motion that correctly leaves the
  ground, such as a jump, and only when the request says so, pass `--no-ground` to both `check`
  and `process`.
- After `process`, make `preview.gif` with `preview`. Each frame lasts 120 ms unless the user
  asks for another speed (`--ms`).

## Procedure

For one asset:

1. **Decide the series and the asset name**, and check for an existing folder (see above).
2. **Build the prompt** from `references/prompts.md` and the series.
3. **Prepare the working folder.** Create a new temporary directory outside the project and
   outside any git repository. Put in it only the prompt file and the one image to attach:
   - a pixel sprite: the reference enlarged with `template --stand reference.png --out <image>`;
   - an illustration or a web image: a copy of `reference.png`;
   - an animation: the template image;
   - a candidate for a new series: no image.
4. **Run Codex** inside the working folder, with the prompt on standard input:

   ```
   codex exec --sandbox workspace-write -c sandbox_workspace_write.exclude_slash_tmp=true -c sandbox_workspace_write.exclude_tmpdir_env_var=true --skip-git-repo-check [--model <model>] --image <the one image> - < prompt.md > codex.stdout 2> codex.stderr
   ```

   `workspace-write` alone also lets Codex write to `/tmp` and `$TMPDIR`; the two `-c` settings
   take those away, so the working folder is the only place it can write. Keep them.
   Add `--model` only when the user named a model; otherwise Codex's default is used. Leave out
   `--image` when there is no image to attach. Set no time limit: wait until Codex exits, however
   long it takes.
5. **If Codex exits non-zero**, stop at once. Keep the working folder and tell the user where it
   is and where the stderr file is. This does not count as a retry. Treat an exit of 0 that left
   no `raw.png` in the working folder the same way.
6. **Check** `raw.png` with `check` (with `--frames`, `--stand`, and `--no-ground` as the asset
   needs). Retry as described in Acceptance and retries.
7. **Process** the accepted raw image into `final.png`; for an animation, also make
   `preview.gif`.
8. **Store** `final.png`, `raw.png`, `prompt.md`, and `preview.gif` (animations) in the asset
   folder, overwriting a remade asset. Then delete the working folder and any other temporary
   files this run made.
9. **Show the user** the finished asset, the preview, and the check result, and let them decide.

## Acceptance and retries

`check` judges:

| Kind | Passes when |
|---|---|
| Pixel sprite | The estimated dot size is within 10% of the expected size, horizontally and vertically; when no dot size can be estimated, this item is undetermined. With `transparent: true`, the four corner dots, picked on the expected grid, are transparent — in each frame, for a sheet |
| Animation | As above, and the top-left cell picked on the expected grid differs from the stand image in at most 5% of its dots, every frame within the frame count has an opaque dot (the reasons name each empty frame by number), and — unless `--no-ground` — aligning the feet pushes no frame above the top of its cell |
| Illustration | With `transparent: true`, a small square at each corner is fully transparent. With `false` there is nothing to judge |
| Web image | The raw image's aspect ratio is within 5% of the ratio of `size` |

Sizes of illustrations and web images are not checked: `process` always produces `size`.

- **`fail`**: generate again automatically with the same prompt, at most twice. Keep each earlier
  raw image in a temporary folder outside the working folder, so the working folder again holds
  only the prompt and the image. When the third attempt also fails, hand over the best result
  with its reasons, processed as usual. Compare the attempts by their `measures`:
  - for a pixel sprite, the one whose larger deviation from the expected dot size, over the two
    axes, is smallest. The deviation is relative to the expected size: horizontally the raw
    image's width ÷ `canvas_dots`, vertically its height ÷ `canvas_dots`;
  - for an animation, the one with the smallest `top_left_diff`;
  - otherwise — when the numbers cannot be compared, such as a `null` dot size, or on a tie — the
    latest attempt.
- **`undetermined`**: not a failure. Do not retry; hand over the result and say that the check
  could not decide.
- A non-zero Codex exit during retries stops everything, as in step 5 of the procedure.
- When `process` refuses a sheet because frames would leave the top of their cells — possible for
  a best result that failed that check — hand over the raw image with the reasons instead of a
  finished sheet.

The user always has the last word. When they reject the result, append their feedback to
`prompt.md`, add it to the prompt, and generate again. These remakes are separate from the
automatic retries and have no limit; each one overwrites the previous result.

## Files and cleanup

| What | Where | How long |
|---|---|---|
| Series definition, reference image, assets | the series folder in the project | until the user deletes them; remakes overwrite, and git keeps earlier versions |
| Working folder and attempt files | a temporary directory | deleted after success; kept only when Codex exits non-zero |
| Codex's own copies of generated images and its sessions | Codex's home directory | left to Codex; never touch them |

## Where the user decides

| Moment | The user sees | The user decides |
|---|---|---|
| New series | the three candidates | which one becomes the reference |
| Asset finished | the asset, the preview, the check result | adopt it, or give feedback and remake |
| Automatic retries used up | the best result and the reasons it failed | adopt it, or give feedback and remake |
| Asset name taken | the existing asset name | whether to overwrite |
| Codex failed | the working folder and stderr file locations | investigate, or try again |

## Judgment

**Why the script and not the prompt handles numbers.** Image models draw well but do not keep
sizes, ratios, or dot grids, and the same request does not give the same look twice. Asking in the
prompt does not fix that; a fixed script does, the same way every time.

**Why one attached image.** The reference image carries the look and the template image carries
the character and the layout. One image per run keeps what is sent small and the instruction
unambiguous.

**Why no confirmation before generating.** The user asks roughly and generation takes minutes.
Showing each prompt for approval would slow every asset down; the prompt is kept in `prompt.md`
instead, and the user judges the result.

**Why a separate working folder.** Running Codex inside the project would expose the project's
files and let Codex write into it. The working folder holds only what is meant to be sent, and
the sandbox limits writing to it.

**Why no time limit.** Stopping Codex reliably needs machinery this skill does not have, and the
retry limit already bounds the total time.
