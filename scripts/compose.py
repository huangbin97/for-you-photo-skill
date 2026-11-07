#!/usr/bin/env python3
"""Crop, color-correct and stack a generated upper photo with an original lower photo."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance


def crop_box(value):
    try:
        box = tuple(int(x) for x in value.split(','))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('crop must be left,top,right,bottom') from exc
    if len(box) != 4 or not (0 <= box[0] < box[2] and 0 <= box[1] < box[3]):
        raise argparse.ArgumentTypeError('crop must have positive area and nonnegative coordinates')
    return box


def load_image(path):
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert('RGB')


def apply_curves(image, data):
    if not isinstance(data, dict) or set(data) != {'r', 'g', 'b'}:
        raise ValueError('curves JSON must contain exactly r, g, b')
    tables = []
    for channel in ('r', 'g', 'b'):
        points = data[channel]
        if not isinstance(points, list) or len(points) < 2:
            raise ValueError('each curve needs at least two [input,output] points')
        for point in points:
            if not isinstance(point, list) or len(point) != 2 or any(type(v) is not int or not 0 <= v <= 255 for v in point):
                raise ValueError('curve coordinates must be integers from 0 to 255')
        if points[0][0] != 0 or points[-1][0] != 255:
            raise ValueError('curves must cover input range 0..255')
        if any(b[0] <= a[0] or b[1] < a[1] for a,b in zip(points, points[1:])):
            raise ValueError('input values must increase; output values must not decrease')
        table = []
        j = 0
        for value in range(256):
            while j + 1 < len(points) - 1 and value > points[j + 1][0]:
                j += 1
            x0,y0 = points[j]
            x1,y1 = points[j + 1]
            table.append(round(y0 + (value-x0)*(y1-y0)/(x1-x0)))
        tables.extend(table)
    return image.point(tables)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upper', required=True, type=Path)
    parser.add_argument('--lower', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--lower-crop', type=crop_box, help='coordinates AFTER EXIF orientation')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--panel-height', type=int, default=800)
    parser.add_argument('--upper-curves', type=Path, help='optional observed RGB correction JSON')
    parser.add_argument('--global-brightness', type=float, default=1.0)
    parser.add_argument('--global-contrast', type=float, default=1.0)
    parser.add_argument('--global-saturation', type=float, default=1.0)
    args = parser.parse_args()
    try:
        if not 0 < args.panel_height < args.width <= 8192:
            raise ValueError('require 0 < panel-height < width <= 8192')
        if any(not 0.9 <= v <= 1.1 for v in (args.global_brightness,args.global_contrast,args.global_saturation)):
            raise ValueError('global adjustment factors must be 0.9..1.1; default 1.0')
        if args.output.suffix.lower() != '.png':
            raise ValueError('output must be a PNG')
        base = args.output.with_suffix('')
        pre = base.with_name(base.name + '.before-global.png')
        record = base.with_name(base.name + '.json')
        paths = [args.output,pre,record]
        if any(path.exists() for path in paths):
            raise ValueError('output or companion files already exist; choose a new output filename')
        if any(path.resolve() in {args.upper.resolve(),args.lower.resolve()} for path in paths):
            raise ValueError('never overwrite reference images')
        upper,lower = load_image(args.upper),load_image(args.lower)
        box = args.lower_crop or (0,0,*lower.size)
        if box[2] > lower.width or box[3] > lower.height:
            raise ValueError('lower crop is outside the oriented image')
        cropped = lower.crop(box)
        if abs(cropped.width / cropped.height - args.width / args.panel_height) > 0.005:
            raise ValueError('lower crop must match target panel ratio within 0.5%; choose a subject-aware crop explicitly')
        curves = None
        if args.upper_curves:
            curves = json.loads(args.upper_curves.read_text(encoding='utf-8'))
            upper = apply_curves(upper,curves)
        size = (args.width,args.panel_height)
        upper = ImageOps.fit(upper,size,method=Image.Resampling.LANCZOS)
        # Ratio is validated above; only proportional resize plus <=1px rounding crop.
        lower_panel = ImageOps.fit(cropped,size,method=Image.Resampling.LANCZOS)
        result = Image.new('RGB',(args.width,2*args.panel_height))
        result.paste(upper,(0,0))
        result.paste(lower_panel,(0,args.panel_height))
        if result.crop((0,args.panel_height,args.width,2*args.panel_height)).tobytes() != lower_panel.tobytes():
            raise ValueError('lower panel verification failed')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        result.save(pre)
        # One contrast pivot across both panels, not separate per-panel processing.
        result = ImageEnhance.Brightness(result).enhance(args.global_brightness)
        result = ImageEnhance.Contrast(result).enhance(args.global_contrast)
        result = ImageEnhance.Color(result).enhance(args.global_saturation)
        result.save(args.output)
        record.write_text(json.dumps({'lower_oriented_size':lower.size,'lower_crop':box,'panel_size':size,'upper_curves':curves,'global':{'brightness':args.global_brightness,'contrast':args.global_contrast,'saturation':args.global_saturation},'lower_verified_before_global':True},ensure_ascii=False,indent=2),encoding='utf-8')
        print(args.output)
    except (ValueError,OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
