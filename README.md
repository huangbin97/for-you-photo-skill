# For You Photo Skill

Turn two photos into a natural “taking your photo” diptych, with coordinated outfits, realistic poses, and consistent lighting and color.

Create a vertically stacked “I’m taking your photo” diptych from two images. Generate only the upper image of the photographer; use a cropped version of the original second photo for the lower image.

## Output and Rules

- Image 1 is the identity reference for photographer A; Image 2 provides the original photo and scene reference for subject B.
- Stack two landscape images of equal width and height. Each panel defaults to a 3:2 aspect ratio, producing a 3:4 image overall; you may adjust the shared landscape aspect ratio to suit the subjects.
- Preserve A’s recognizable identity, use a plausible shooting angle, and keep the shoulders, neck, and hands natural. Subtle contour refinement and light reduction of localized fine lines are allowed.
- Preserve natural skin texture and normal sharpness. Check the pupils, hair strands, and camera occlusion, and avoid oversharpening or excessive skin smoothing.
- Match the upper image’s color to the lower image. Do not redraw the lower image; only subtle global color adjustments may be applied to the final composite.

## Usage

### Tools That Support Skills

Download the repository and import the folder containing `SKILL.md`, `references/`, `scripts/`, and `requirements.txt` according to your host tool’s instructions. If the tool requires the folder name to match the skill name, rename the local folder to `make-couple-photo-diptych`. Installation locations and invocation methods depend on the host tool; this repository does not claim verified compatibility with every tool.

After uploading two images, say:

> Use the For You Photo skill. The first image is the photographer, and the second is the subject. Generate only the upper, photographer-view image; preserve the original second photo for the lower panel. Stack the two landscape images vertically, with natural skin texture, realistic poses, and consistent color.

### Regular Chat or Image-Generation Tools

Use the [portable prompt](references/portable-prompt.md) and upload both reference images. If the tool can only generate images, save the generated upper image first, then run the composition script locally or in a tool that supports code execution.

### Deterministic Composition

Requires Python 3.10+ and Pillow. This script does not call any paid APIs, generate people, or retouch their appearance.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/compose.py --upper inputs/upper.png --lower inputs/person-b.jpg --lower-crop 0,300,1440,1260 --width 1200 --panel-height 800 --output outputs/diptych.png
```

Crop coordinates must be chosen for the actual photo; the example applies only to images with matching dimensions. You can omit `--lower-crop` when the lower image is already a landscape image with the required aspect ratio. The script rejects clearly invalid aspect ratios, out-of-bounds crops, and attempts to overwrite existing output files.

Optionally, use `--upper-curves curves.json` to apply observation-driven RGB curve adjustments to the upper image. The example below is an **identity curve that makes no color changes**, not a general-purpose filter:

```json
{"r": [[0, 0], [255, 255]], "g": [[0, 0], [255, 255]], "b": [[0, 0], [255, 255]]}
```

Global brightness, contrast, and saturation default to 1.0 and can be adjusted subtly within the 0.9–1.1 range. The output includes the final PNG, the composite before global color adjustment, and a JSON file containing the parameters. Color consistency and subject quality require review by a person or vision model; the script does not validate them automatically.

## Capabilities and Limitations

A complete run requires reference-based image generation or editing, image-viewing capability, and an environment that can run the script. The skill does not include an image-generation model, API keys, or paid subscriptions, and results will vary between models. An AI without image-generation capability can prepare the prompt but cannot produce the finished image independently. Errors in localized lighting or in the structure of eyes and hands require image-editing capability to correct.

## Files

- `SKILL.md`: Complete workflow and acceptance criteria.
- `references/prompt-template.md`: Detailed template for generating the upper image.
- `references/portable-prompt.md`: Simplified, copy-ready prompt.
- `scripts/compose.py`: Cropping, optional color adjustment, composition, and lower-image pixel validation.
- `requirements.txt`: Image-processing dependencies.

This repository contains no private photos or secrets. Use only images you have the right to process and share. Generated scenes are synthetic creations and do not imply that the depicted events actually occurred.
