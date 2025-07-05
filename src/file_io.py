import os
import json
import shutil
import sys
import numpy as np

from collections import deque, Counter
from tqdm import tqdm
from PIL import Image
from src.util.config import OUTPUT_DIR, MINECRAFT_JAR_FONT_DIR
from src.util.constants import BITMAP_COLUMNS, BITMAP_GLYPH_SIZE
from src.util.functions import get_unicode_codepoint

def convert_tile_into_svg(tile):
    # Read image
    width, height = tile["size"]

    # Write <rect> elements left-aligned
    svg_rects = [
        f'<rect x="{x}" y="{y}" width="1" height="1" />'
        for y, row in enumerate(tile["pixels"]["grid"])
        for x, val in enumerate(row)
        if val >= 1
    ]
    # TODO: BOLD AND ITALIC
    #transform = f"matrix(1,0,{ITALIC_SHEAR_FACTOR},1,0,0)"

    tile["svg"] = f'''<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">
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
    pixel_grid = np.full((height, width), -999, dtype=int) # Empty grid

    def update_grid(queue, bit_match, next_label, neighbours = None):
        while queue:
            cy, cx = queue.popleft()

            # Ensure the current pixel is labeled
            if pixel_grid[cy, cx] == -999:
                pixel_grid[cy, cx] = next_label

            for dy, dx in neighbours or [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx

                if 0 <= ny < height and 0 <= nx < width:
                    if bitmap_grid[ny, nx] == bit_match and pixel_grid[ny, nx] == -999:
                        pixel_grid[ny, nx] = next_label
                        queue.append((ny, nx))

    def label_groups(bit_match, increment, neighbours = None):
        next_label = 0 + increment
        labels = []

        for y in range(height):
            for x in range(width):
                if bitmap_grid[y, x] == bit_match and pixel_grid[y, x] == -999:
                    q = deque()
                    q.append((y, x))
                    pixel_grid[y, x] = next_label
                    labels.append(next_label)
                    update_grid(q, bit_match, next_label, neighbours)
                    next_label += increment

        return labels

    # Label glyph groups as 1 and above
    path_labels = label_groups(1, 1, [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])

    # Flood-fill outer background as 0
    q = deque()
    for x in range(width):
        if bitmap_grid[0, x] == 0: q.append((0, x))
        if bitmap_grid[height - 1, x] == 0: q.append((height - 1, x))
    for y in range(height):
        if bitmap_grid[y, 0] == 0: q.append((y, 0))
        if bitmap_grid[y, width - 1] == 0: q.append((y, width - 1))
    update_grid(q, 0, 0)

    hole_labels = label_groups(0, -1)

    def trace_pixel_edge_turns(pixel_grid, label):
        # Get all (x, y) tile coords for the hole
        coords = [tuple([x, y]) for y, x in np.argwhere(pixel_grid == label)]
        black_set = set(coords)

        def is_valid_pixel(x, y):
            return (x, y) in black_set

        # Get edge segments around each black pixel
        def get_edges(x, y):
            # edges are (from, to) pairs going clockwise around a square
            return [((x, y), (x+1, y)),
                    ((x+1, y), (x+1, y+1)),
                    ((x+1, y+1), (x, y+1)),
                    ((x, y+1), (x, y))]

        edge_count = {}
        for x, y in black_set:
            if not is_valid_pixel(x, y):
                continue
            for edge in get_edges(x, y):
                if edge[::-1] in edge_count:
                    edge_count[edge[::-1]] -= 1
                else:
                    edge_count[edge] = edge_count.get(edge, 0) + 1

        # Only keep boundary edges (ones not shared by two valid pixels)
        boundary_edges = {e for e, count in edge_count.items() if count > 0}
        if not boundary_edges:
            return {"coords": coords, "corners": []}

        # Start from top-left most edge
        start_edge = min(boundary_edges, key=lambda e: (e[0][1], e[0][0]))
        path = [start_edge[0]]
        path = []
        current_edge = start_edge
        visited = set()

        # Right-hand rule
        def direction(a, b): return b[0] - a[0], b[1] - a[1]
        def rotate_right(d): return d[1], -d[0]
        def rotate_left(d): return -d[1], d[0]

        while True:
            a, b = current_edge
            dir = direction(a, b)
            found = False
            for turn in [rotate_right, lambda d: d, rotate_left]:
                ndir = turn(dir)
                next_point = (b[0] + ndir[0], b[1] + ndir[1])
                next_edge = (b, next_point)
                if next_edge in boundary_edges and next_edge not in visited:
                    path.append(b)
                    visited.add(next_edge)
                    current_edge = next_edge
                    found = True
                    break
            if not found or current_edge == start_edge:
                break

        return path

    def extract_corners_from_path(path):
        def direction(a, b):
            return b[0] - a[0], b[1] - a[1]

        corners = []
        n = len(path)

        if n < 3:
            return path.copy()  # fallback

        for i in range(len(path)):
            # prev = path[i - 1]
            # curr = path[i]
            # next = path[i + 1]
            prev = path[(i - 1) % n]
            curr = path[i]
            next = path[(i + 1) % n]
            dir1 = direction(prev, curr)
            dir2 = direction(curr, next)
            if dir1 != dir2:
                corners.append(curr)

        return corners

    def get_path_data(pixel_grid, label):
        #coords = [tuple([x, y]) for y, x in np.argwhere(pixel_grid == label)]
        coords = trace_pixel_edge_turns(pixel_grid, label)
        return {
            "coords": coords,
            "corners": extract_corners_from_path(coords)
        }

    tile["pixels"] = {
        "grid": pixel_grid,
        "paths": {label: get_path_data(pixel_grid, label) for label in path_labels},
        "holes": {label: get_path_data(pixel_grid, label) for label in hole_labels}
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
        bitmap = read_provider_bitmap(provider)
        tiles = []

        # Calculate tile dimensions
        width, height = bitmap.size
        glyph_width = width / BITMAP_COLUMNS

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
                    "size": (glyph_width, provider.get("height")),
                    "ascent": provider.get("ascent", 0),
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
                "ascent": provider.get("ascent", 0),
                "height": provider.get("height", BITMAP_GLYPH_SIZE),
                "chars": chars,
                "file_name": file_name,
                "file_path": MINECRAFT_JAR_FONT_DIR + "/" + file_name,
                "name": name,
                "output": output,
                "tiles": []
            })

    return providers

def clean_output_dir():
    print("🧹 Cleaning output directory...")
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
