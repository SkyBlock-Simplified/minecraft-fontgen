import os

from PIL import Image, ImageDraw, ImageFont

from minecraft_fontgen.functions import log

def write_preview_image(font_files, output_dir):
    """Renders alphabet and numbers for each font style onto a preview PNG."""
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
            log(f"→ ⚠️ Could not load {name} for preview: {e}")
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

    output_path = os.path.join(output_dir, "preview.png")
    img.save(output_path)
    log(f"🖼️ Preview image saved to {output_path}")

    # Write comparison image: Regular/Galactic/Illageralt stacked per case
    compare_styles = ["Regular", "Galactic", "Illageralt"]
    compare_fonts = [(n, f) for n, f in fonts if any(n.endswith(s) for s in compare_styles)]
    if len(compare_fonts) >= 2:
        write_compare_image(compare_fonts, output_dir, font_size, padding, label_font)


def write_compare_image(fonts, output_dir, font_size, padding, label_font):
    """Renders uppercase block then lowercase block, with font styles stacked vertically in each."""
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"
    lower = "abcdefghijklmnopqrstuvwxyz 0123456789"
    line_height = font_size + 8
    label_height = 24
    block_height = label_height + line_height * len(fonts) + padding

    # Measure max text width and label width
    max_width = 0
    label_width = 0
    for name, font in fonts:
        for text in (upper, lower):
            bbox = font.getbbox(text)
            max_width = max(max_width, bbox[2] - bbox[0])
        lb = label_font.getbbox(name.split("-")[-1])
        label_width = max(label_width, lb[2] - lb[0])

    img_width = max_width + label_width + padding * 2 + 8
    img_height = block_height * 2 + padding
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Draw uppercase block
    y = padding
    draw.text((padding, y), "Uppercase", fill="gray", font=label_font)
    y += label_height
    for name, font in fonts:
        draw.text((padding, y), upper, fill="black", font=font)
        draw.text((max_width + padding + 4, y + 4), name.split("-")[-1], fill="gray", font=label_font)
        y += line_height

    # Draw lowercase block
    y += padding
    draw.text((padding, y), "Lowercase", fill="gray", font=label_font)
    y += label_height
    for name, font in fonts:
        draw.text((padding, y), lower, fill="black", font=font)
        draw.text((max_width + padding + 4, y + 4), name.split("-")[-1], fill="gray", font=label_font)
        y += line_height

    output_path = os.path.join(output_dir, "compare.png")
    img.save(output_path)
    log(f"🖼️ Compare image saved to {output_path}")
