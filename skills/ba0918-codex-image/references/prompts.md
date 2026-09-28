# Prompt skeletons

Build every prompt from one of the four skeletons below. Replace each `<...>` with what the series
and the request give, drop lines that do not apply, and keep every line marked **(always)**.
Write the prompt in plain sentences; Codex reads it as an instruction to generate one image.

Some wordings matter more than they look, and only work when they are in the prompt:

- **Carry over / do not carry over.** With an attached reference, list both explicitly. Without
  the second list, Codex copies the reference's eyes, outline, and pose into the new subject.
- **Save unchanged.** Without it, Codex resizes, crops, or converts the image, differently each
  time, and the post-processing then works on something unpredictable.
- **No effect frames.** Without it, animation sheets gain white flashes and fades that are drawn
  differently every time and whose translucency does not survive post-processing.
- **Margin.** A web image is cropped from the centre afterwards, so the subject has to stay clear
  of the edges.

The common closing lines, used by every skeleton:

```
Generate exactly one image. (always)
Save the generated image as raw.png in the current working folder, exactly as generated: do not
scale, crop, convert, or edit it in any way. (always)
Do not create or change any other file.
```

## 1. Single asset with a reference (stand image, illustration)

```
Create <what: "a stand image of a bat character", "an illustration of a forest shrine">.

The attached image is the reference for this series.
Carry over from it: <from the series.md body: drawing style, palette, line work, shading>.
Do not carry over: <from the series.md body: shapes, face and eyes, pose, the subject itself>.
The new subject is <the request, in concrete terms>.

<pixel sprite:>
This is a pixel sprite of exactly <canvas_dots> x <canvas_dots> dots filling the whole square
image. Every dot is a solid square of the same size, one colour each, with no anti-aliasing,
blur, or gradients across a dot. The attached reference is shown at 10 px per dot.
<pixel sprite, transparent: true:>
The background is fully transparent; only the character is opaque. Draw the character standing,
feet near the bottom of the canvas, and keep it inside the canvas.
<pixel sprite, transparent: false:>
Draw the background as part of the sprite, on the same dot grid.

<illustration, transparent: true:>
The background is fully transparent. Keep the subject well away from the corners.
<illustration, transparent: false:>
Draw a full background. Compose for a <size> (<width>:<height>) frame.

<other notes on the look from the series.md body>
<the user's feedback from earlier remakes, one line each>

<common closing lines>
```

## 2. New series candidate (no reference yet)

```
Create <what>, as the first image of a new series of <purpose: "game sprites", "website art">.

Style: <the user's style description>.
Direction for this candidate: <what varies between the three: "warmer palette", "rounder,
shorter proportions", "higher contrast">.

<the same kind lines as skeleton 1: pixel sprite / illustration / web, per the answers given>

<common closing lines>
```

Build three prompts that differ only in the direction line, and generate each in its own working
folder.

## 3. Animation sheet (template image attached)

```
Create an animation sheet of <character> doing <motion: "an attack", "a walk cycle">,
<frames> frames.

The attached template image is the sheet layout: 4 columns and <rows> rows of square cells,
shown at 10 px per dot, each cell <canvas_dots> x <canvas_dots> dots. The top-left cell already
holds the character's stand image; it is frame 1. Draw frames 2 to <frames> in the following
cells, left to right, then top to bottom. Leave the remaining <empty count> cells empty and
transparent.

Keep the character exactly as in frame 1: same shapes, face, palette, and size. Only the pose
changes. Keep every frame's body inside its own cell.
<motion stays on the ground:>
Keep the feet on the same ground line as in frame 1.
<motion leaves the ground, and the request says so:>
The character leaves the ground during the motion; draw the height as it should be.

Every dot is a solid square of the same size as in the template image, one colour each, with no
anti-aliasing, blur, or gradients. The background is fully transparent.
Do not draw effect frames such as white flashes, fades, motion blur, or afterimages.
<only when the user explicitly asked for effects: replace the previous line with what they asked>

Keep the image's layout identical to the template image: the same grid, the same proportions.

<the user's feedback from earlier remakes, one line each>

<common closing lines>
```

## 4. Web image (reference attached)

```
Create <what: "a hero image for the top page showing ...">.

The attached image is the reference for this series.
Carry over from it: <from the series.md body>.
Do not carry over: <from the series.md body: subjects, composition>.

Draw it at an aspect ratio of <width>:<height> (<size>), filling the whole image with no borders.
Keep the main subject and any important detail out of the outer tenth of every edge; that area
may be cropped away.
The image is fully opaque.

<other notes on the look from the series.md body>
<the user's feedback from earlier remakes, one line each>

<common closing lines>
```
