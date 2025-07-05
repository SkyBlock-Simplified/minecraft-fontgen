import os
import json
import shutil
import sys
import numpy as np

from collections import deque, defaultdict, Counter
from tqdm import tqdm
from PIL import Image
from src.util.config import OUTPUT_DIR, MINECRAFT_JAR_FONT_DIR
from src.util.constants import BITMAP_COLUMNS, BITMAP_GLYPH_SIZE
from src.util.functions import get_unicode_codepoint

def convert_tile_into_svg(tile):
    # Read image
    tile_width, tile_height = tile["size"]

    # Write <rect> elements left-aligned
    svg_rects = [
        f'<rect x="{x}" y="{y}" width="1" height="1" />'
        for y, x in tile["pixels"]["coords"]
    ]

    # TODO: BOLD AND ITALIC
    #transform = f"matrix(1,0,{ITALIC_SHEAR_FACTOR},1,0,0)"

    tile["svg"] = f'''<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 {tile_width} {tile_height}" shape-rendering="crispEdges">
    <g fill="black">
        {''.join(svg_rects)}
    </g>
</svg>
'''

    # Save file
    tile["svg_file"] = f"{tile['output']}/regular.svg"
    with open(tile["svg_file"], "w", encoding="utf-8") as f:
        f.write(tile["svg"])

def convert_tile_into_pixels(tile):
    # Convert image to pixels
    bitmap_grid = np.array(tile["bitmap"].convert("L"), dtype=int) # White (255) / Black (0)
    bitmap_grid = (bitmap_grid < 128).astype(np.uint8) # White (0) / Black (1)
    height, width = bitmap_grid.shape

    # Create pixel grid
    pixel_grid = np.zeros((height, width), dtype=int)

    # Replace exterior zeros with twos
    q = deque()
    for x in range(width):
        if bitmap_grid[0, x] == 0: q.append((0, x))
        if bitmap_grid[height - 1, x] == 0: q.append((height - 1, x))
    for y in range(height):
        if bitmap_grid[y, 0] == 0: q.append((y, 0))
        if bitmap_grid[y, width - 1] == 0: q.append((y, width - 1))
    while q:
        y, x = q.popleft()
        if 0 <= y < height and 0 <= x < width:
            if bitmap_grid[y, x] == 0 and pixel_grid[y, x] == 0:
                pixel_grid[y, x] = 2
                q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])

    # Label interior hole pixels with unique number
    hole_labels = []
    next_hole = 3
    for y in range(height):
        for x in range(width):
            if bitmap_grid[y, x] == 0 and pixel_grid[y, x] == 0:
                # Found new hole
                q = deque()
                hole_labels.append(next_hole)
                q.append((y, x))
                pixel_grid[y, x] = next_hole

                while q:
                    cy, cx = q.popleft()

                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx

                        if height > ny >= 0 == bitmap_grid[ny, nx] and width > nx >= 0 == pixel_grid[ny, nx]:
                            pixel_grid[ny, nx] = next_hole
                            q.append((ny, nx))

                next_hole += 1

    tile["pixels"] = {
        "grid": pixel_grid,
        "holes": hole_labels,
        "coords": [(x, y) for y, x in np.argwhere(pixel_grid == 0)]
    }

def crop_tile_from_bitmap(bitmap, tile):
    # Crop tile from bitmap
    x, y = tile["location"]
    width, height = tile["size"]
    px, py = (x * width, y * height)
    tile["bitmap"] = bitmap.crop((px, py, px + width, py + height))

    # Save tile
    tile["bmp_file"] = f"{tile['output']}/glyph.bmp"
    os.makedirs(tile["output"], exist_ok=True)
    tile["bitmap"].save(tile["bmp_file"])

def read_provider_bitmap(provider):
    img = Image.open(provider["file_path"]).convert("RGBA")

    # Composite white glyphs over black background
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255)) # Black background
    img = Image.alpha_composite(bg, img).convert("L") # 1-bit grayscale

    # Invert white glyphs to black
    img = Image.eval(img, lambda x: 255 - x)

    # Binarize to 1-bit: make black glyphs (0) on white (255)
    img = img.point(lambda x: 0 if x < 128 else 255, '1')

    # Copy original and save grayscale
    output_file = provider["output"] + "/" + provider["name"]
    shutil.copyfile(provider["file_path"], output_file + ".png")
    img.save(f"{output_file}_grayscale.png")

    return img

def slice_providers_into_tiles(providers):
    print(f"✂️ Slicing bitmap providers into tiles...")

    for provider in providers:
        print(f"→ 🖼️ Reading '{provider['file_name']}'...")

        #if provider["name"] != "ascii": # TODO: TEMPORARY
        #    continue

        bitmap = read_provider_bitmap(provider)
        tiles = []

        with tqdm(enumerate(provider["chars"]), total=len(provider["chars"]),
                  desc=" → 🔣 Tiles", unit="tile",
                  ncols=80, leave=False, file=sys.stdout) as tiles_progress:
            for i, unicode in tiles_progress:
                # Skip .notdef
                codepoint = get_unicode_codepoint(unicode)
                if codepoint == 0x0000:
                    continue

                # Update progress bar
                tiles_progress.set_description(f" → 🔣 0x{codepoint:02X}")

                # Collate tile data
                tile_row = i // BITMAP_COLUMNS
                tile_column = i % BITMAP_COLUMNS
                tile = {
                    "unicode": unicode,
                    "codepoint": codepoint,
                    "size": (BITMAP_GLYPH_SIZE, provider.get("height") or BITMAP_GLYPH_SIZE),
                    "location": (tile_column, tile_row),
                    "output": f"{provider['output']}/tiles/{tile_row:02}_{tile_column:02}_{codepoint:04X}"
                }
                tiles.append(tile)

                # Crop tile from bitmap
                crop_tile_from_bitmap(bitmap, tile)

                # Create pixel grid and collect hole data
                convert_tile_into_pixels(tile)

                # Create svg files
                convert_tile_into_svg(tile)

            provider["tiles"] = tiles

def read_providers_from_json_file(json_file):
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
            output = OUTPUT_DIR + "/" + name

            # Create provider directory
            os.makedirs(output, exist_ok=True)

            # Read unicode characters
            chars = [char for row in provider.get("chars", []) for char in row]
            print(f" → 🔢 Detected {len(chars)} unicode characters in '{name}'...")

            providers.append({
                "ascent": provider.get("ascent") or 0,
                "chars": chars,
                "file_name": file_name,
                "file_path": MINECRAFT_JAR_FONT_DIR + "/" + file_name,
                "name": name,
                "output": output
            })

    return providers

def clean_output_dir():
    print("🧹 Cleaning output directory...")
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
