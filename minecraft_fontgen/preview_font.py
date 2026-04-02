import os

from PIL import Image, ImageDraw, ImageFont

from minecraft_fontgen.functions import log

# Icon glyphs grouped by source file from MinecraftImageGenerator/data/
ICON_GROUPS = [
    ("stats", "\u2741\u2764\u2748\u2742\u2726\u270E\u2623\u2620\u2694\u2AFD"
              "\u2604\u2668\u2763\u272F\u2663\u03B1\u2602\u0E51\u2E15\u24C5"
              "\u2727\u2618\u2E0E\u02AC\u24C8\u262F\u0444\u26A1\u259A\u2693"
              "\u2654\u0D60\u26C3\u2744\u222E\u26B6\u274D\u16F7\u2743"),
    ("flavor", "\u2763\u2620\u0F15\u0416\u2708\u262E\u2693\u2643\u2699\u2682"
               "\u2663\u2299\u2603\u2744\u2730\u2668\u2646\u273F\u0D60\u26E8"
               "\U0001F9B4\u263D\u26CF\u2E19\u2662\u1805\u0DAE\uAA03\u0FC9"
               "\u127E\u2692"),
    ("gemstones", "\u2764\u2748\u2742\u270E\u2741\u2618\u2E15\u2727\u2620"
                  "\u03B1\u2694\u2624\u2726"),
    ("icons", "\u2022\u24C4\u24E9\u272A\u269A\u24B7\u23E3\u2706\uA56E\uA1A4"
              "\u096A\u2E19\u238B\u2714\u2716\u26C3"),
]


def write_preview_image(font_files, output_dir):
    """Renders A-Z, a-z, and 0-9 for each font style onto a preview PNG."""
    lines = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "abcdefghijklmnopqrstuvwxyz",
        "0123456789",
    ]
    font_size = 48
    padding = 20
    label_height = 24
    line_height = font_size + 8
    block_height = label_height + line_height * len(lines) + padding

    # Measure max width across all fonts
    max_width = 0
    fonts = []
    for path in font_files:
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            font = ImageFont.truetype(path, font_size)
        except Exception as e:
            log(f"\u2192 \u26a0\ufe0f Could not load {name} for preview: {e}")
            continue
        fonts.append((name, font))
        for line in lines:
            bbox = font.getbbox(line)
            max_width = max(max_width, bbox[2] - bbox[0])

    if not fonts:
        return

    img_width = max_width + padding * 2
    img_height = block_height * len(fonts) + padding
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    try:
        label_font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        label_font = ImageFont.load_default()

    y = padding
    for name, font in fonts:
        draw.text((padding, y), name, fill="gray", font=label_font)
        y += label_height
        for line in lines:
            draw.text((padding, y), line, fill="black", font=font)
            y += line_height
        y += padding

    output_path = os.path.join(output_dir, "preview-ascii.png")
    img.save(output_path)
    log(f"\U0001f5bc\ufe0f Preview image saved to {output_path}")


def write_render_image(font_file, output_dir):
    """Renders Unicode icon glyphs grouped by source file onto a dark-background preview PNG."""
    font_size = 48
    padding = 20
    label_height = 24
    line_height = font_size + 8

    try:
        font = ImageFont.truetype(font_file, font_size)
    except Exception as e:
        log(f"\u2192 \u26a0\ufe0f Could not load font for unicode preview: {e}")
        return

    try:
        label_font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        label_font = ImageFont.load_default()

    # Build spaced text for each group
    groups = [(label, " ".join(icons)) for label, icons in ICON_GROUPS]

    # Measure dimensions
    max_width = 0
    for label, text in groups:
        bbox = font.getbbox(text)
        max_width = max(max_width, bbox[2] - bbox[0])

    block_height = label_height + line_height + padding
    img_width = max_width + padding * 2
    img_height = block_height * len(groups) + padding
    img = Image.new("RGB", (img_width, img_height), (54, 57, 63))
    draw = ImageDraw.Draw(img)

    y = padding
    for label, text in groups:
        draw.text((padding, y), label, fill=(160, 160, 160), font=label_font)
        y += label_height
        draw.text((padding, y), text, fill=(255, 255, 255), font=font)
        y += line_height
        y += padding

    output_path = os.path.join(output_dir, "preview-unicode.png")
    img.save(output_path)
    log(f"\U0001f5bc\ufe0f Unicode preview saved to {output_path}")
