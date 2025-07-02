import os
import json
import shutil

from PIL import Image
from src.util.config import OUTPUT_PATH, MINECRAFT_JAR_FONT_DIR
from src.util.constants import BITMAP_COLUMNS, BITMAP_GLYPH_SIZE
from src.util.functions import progress_bar, get_unicode_codepoint

def read_provider_bitmap(provider):
    print(f"→ 🖼️ Reading '{provider['file_name']}'...")
    img = Image.open(provider["file_path"]).convert("RGBA")
    width, height = img.size
    bmp_tiles = []

    print(f"→ 🏁 Converting to grayscale...")
    # Composite white glyphs over black background
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255)) # Black background
    img = Image.alpha_composite(bg, img).convert("L") # Grayscale

    # Invert white glyphs to black
    img = Image.eval(img, lambda x: 255 - x)

    # Binarize to 1-bit: make black glyphs (0) on white (255)
    img = img.point(lambda x: 0 if x < 128 else 255, '1')

    # Copy original and save grayscale
    output_file = provider["output"] + "/" + provider["name"]
    shutil.copyfile(provider["file_path"], output_file + ".png")
    img.save(f"{output_file}_grayscale.png")

    return img

def slice_bitmap_into_bmp(provider):
    # Image and glyph dimensions
    image = provider["image"]
    width, height = image.size
    glyph_width = provider["glyph_width"]
    glyph_height = provider["glyph_height"]
    bmp_tiles = []

    print(f"→ 🧩 Creating BMP tiles...")
    for idx, y in enumerate(range(0, height, glyph_height)):
        for x in range(0, width, glyph_width):
            tile_row = y // glyph_width
            tile_column = x // glyph_height
            index = idx * BITMAP_COLUMNS + (tile_column)
            tile = image.crop((x, y, x + glyph_width, y + glyph_height))

            # Skip tiles without corresponding Unicode entry
            if index >= len(provider["chars"]):
                print(f" → ⚠️ Failed to load glyph {index}@{tile_row},{tile_column}.")
                continue

            # Load glyph
            codepoint = get_unicode_codepoint(provider["chars"][index])
            tile_dir = f"{provider['tile_output']}/{tile_row:02}_{tile_column:02}_{codepoint:04X}"
            tile_path = f"{tile_dir}/glyph.bmp"

            # Create tile directory
            os.makedirs(tile_dir, exist_ok=True)

            # Save tile
            tile.save(tile_path)
            bmp_tiles.append(tile_path)

    return bmp_tiles

def convert_bmp_into_svg(provider):
    print("→ ✒️ Creating SVG files...")
    svg_files = []
    total_chars = len(provider["chars"])
    index = 0

    for bmp_path in provider["bmp_tiles"][:total_chars]:
        # Show progress bar
        progress_bar(index, total_chars)
        index += 1

        # Read image
        img = Image.open(bmp_path).convert("1") # Ensure 1-bit black/white
        width, height = img.size
        glyph_width = provider["glyph_width"]
        glyph_height = provider["glyph_height"]
        svg_elements = []

        # Collect black pixels
        black_pixels = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if img.getpixel((x, y)) == 0
        ]

        # Write <rect> elements left-aligned
        for x, y in black_pixels:
            #sheared_x = x + ITALIC_SHEAR_FACTOR * y
            svg_elements.append(f'<rect x="{x}" y="{y}" width="1" height="1" />')
            #svg_elements.append(f'<rect x="{x+1}" y="{y}" width="1" height="1" />')

        # TODO: ITALIC TRANSFORMATION
        #transform = f"matrix(1,0,{ITALIC_SHEAR_FACTOR},1,0,0)"
        svg_content = f'''<?xml version="1.0" standalone="no"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 {glyph_width} {glyph_height}" shape-rendering="crispEdges">
        <g fill="black">
            {''.join(svg_elements)}
        </g>
    </svg>
    '''

        # Save file
        svg_file = os.path.dirname(bmp_path) + "/regular.svg" # TODO: BOLD AND ITALIC
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_content)

        svg_files.append(svg_file)

    # Finish the progress bar
    progress_bar(total_chars, total_chars)
    print()

    return svg_files

def read_json_file(json_file):
    print(f"🧩 Parsing '{json_file}'...")

    with open(json_file, "rb") as f:
        raw_bytes = f.read()

    # Decode and parse JSON while preserving surrogate pairs
    print("→ 🛠️ Decoding json...")
    raw_text = raw_bytes.decode("utf-8", errors="surrogatepass")
    data = json.loads(raw_text)

    print("→ 🛠️ Parsing bitmap providers...")
    providers = []
    for provider in data.get("providers", []):
        if provider.get("type") == "bitmap" and "chars" in provider:
            file_name = provider.get("file", "minecraft:font/").split("minecraft:font/")[-1]
            name = os.path.splitext(file_name)[0]
            output = OUTPUT_PATH + "/" + name

            # Read unicode characters
            flat_chars = [char for row in provider.get("chars", []) for char in row]
            print(f" → 🔢 Detected {len(flat_chars)} unicode characters in '{name}'...")

            entry = {
                "chars": flat_chars,
                "ascent": provider.get("ascent") or 0,
                "glyph_height": provider.get("height") or BITMAP_GLYPH_SIZE,
                "glyph_width": BITMAP_GLYPH_SIZE,
                "name": name,
                "file_name": file_name,
                "file_path": MINECRAFT_JAR_FONT_DIR + file_name,
                "output": output,
                "tile_output": output + "/" + "tiles"
            }

            # Create output directory
            os.makedirs(entry["tile_output"], exist_ok=True)
            providers.append(entry)

    print(f"✂️ Slicing bitmap providers into tiles...")
    for provider in providers:
        provider["image"] = read_provider_bitmap(provider)
        provider["bmp_tiles"] = slice_bitmap_into_bmp(provider)
        provider["svg_files"] = convert_bmp_into_svg(provider)

    return providers

def clean_output_dir():
    print("🧹 Cleaning output directory...")
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
