import os
import shutil
import sys
import numpy as np

from collections import deque, OrderedDict
from tqdm import tqdm
from PIL import Image
from minecraft_fontgen.config import COLUMNS_PER_ROW, DEFAULT_GLYPH_SIZE, OUTPUT_DIR, MINECRAFT_JAR_DIR, WORK_DIR, UNITS_PER_EM, UNIFONT_DEBUG_SVG, TEXTURE_PATH
from minecraft_fontgen.functions import get_unicode_codepoint, in_unifont_ranges, log, is_silent, parse_json


def _write_tile_svg(grid, size, output_file):
    """Renders a pixel grid as an SVG file with 1x1 rect elements."""
    width, height = size

    svg_rects = [
        f'<rect x="{x}" y="{y}" width="1" height="1" />'
        for y, row in enumerate(grid)
        for x, val in enumerate(row)
        if val >= 1
    ]

    svg = {
        "xml": f'''<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">
    <g fill="black">
        {''.join(svg_rects)}
    </g>
</svg>
''',
        "file": output_file
    }

    with open(svg["file"], "w", encoding="utf-8") as f:
        f.write(svg["xml"])

    return svg

def convert_tile_into_svg(tile):
    """Generates SVG debug output for both regular and bold styles of a tile."""
    return {
        "regular": _write_tile_svg(tile["pixels"]["regular"]["grid"], tile["size"], f"{tile['output']}/regular.svg"),
        "bold": _write_tile_svg(tile["pixels"]["bold"]["grid"], tile["size"], f"{tile['output']}/bold.svg")
    }

def convert_tile_into_pixels(tile):
    """Converts a tile's bitmap image to pixel data for both regular and bold styles."""
    return {
        "regular": _convert_tile_into_pixels(tile, False),
        "bold": _convert_tile_into_pixels(tile, True)
    }

def _bitmap_to_pixel_data(bitmap_grid, bold: bool = False):
    """Traces contours from a binary bitmap grid using flood-fill labeling and right-hand edge
    tracing. Returns pixel data with labeled grid, path corners, hole corners, advance width,
    and left side bearing for font glyph construction.
    """
    height, width = bitmap_grid.shape
    pixel_grid = np.full((height, width), -999, dtype=int) # Create empty grid

    if bold: # iterate from bottom to top, right to left
        for i in range(bitmap_grid.shape[0] - 1, -1, -1):
            for j in range(bitmap_grid.shape[1] - 1, -1, -1):
                if bitmap_grid[i, j] == 1 and j + 1 < bitmap_grid.shape[1] and bitmap_grid[i, j + 1] == 0:
                    bitmap_grid[i, j + 1] = 1 # copy 1 to the right

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

        # Start from the top-left most edge
        start_edge = min(boundary_edges, key=lambda e: (e[0][1], e[0][0]))
        path = [] # [start_edge[0]]
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
            prev = path[(i - 1) % n]
            curr = path[i]
            next = path[(i + 1) % n]
            dir1 = direction(prev, curr)
            dir2 = direction(curr, next)
            if dir1 != dir2:
                corners.append(curr)

        return corners

    def get_path_data(pixel_grid, label):
        coords = trace_pixel_edge_turns(pixel_grid, label)
        return {
            "coords": coords,
            "corners": extract_corners_from_path(coords)
        }

    # Determine glyph sides
    col_sums = pixel_grid.sum(axis=0) # Sum each column to see where 1's exist
    col_ones = np.where(col_sums > 0)[0] # Find indices where there is at least one 1 in that column
    min_x = col_ones[0] if len(col_ones) > 0 else 0
    max_x = col_ones[-1] if len(col_ones) > 0 else DEFAULT_GLYPH_SIZE - 1
    width = col_ones[-1] - col_ones[0] + 1 if len(col_ones) > 0 else DEFAULT_GLYPH_SIZE

    return {
        "bitmap": bitmap_grid,
        "grid": pixel_grid,
        "width": (max_x - min_x + 1),
        "lsb": min_x,
        "advance": (min_x + width + 1),
        "paths": {label: get_path_data(pixel_grid, label) for label in path_labels},
        "holes": {label: get_path_data(pixel_grid, label) for label in hole_labels}
    }

def _convert_tile_into_pixels(tile, bold: bool = False):
    """Converts a tile's PIL bitmap image to a binary numpy grid and processes it into pixel data."""
    bitmap_grid = np.array(tile["bitmap"]["image"].convert("L"), dtype=int)
    bitmap_grid = (bitmap_grid < 128).astype(np.uint8)
    return _bitmap_to_pixel_data(bitmap_grid, bold)

def crop_tile_from_bitmap(bitmap, tile):
    """Crops a single glyph tile from a full provider bitmap and saves it to disk."""
    x, y = tile["location"]
    width, height = tile["size"]
    glyph_width = int(width)
    px, py = (x * glyph_width, y * height)

    bitmap = {
        "image": bitmap.crop((px, py, px + glyph_width, py + height)),
        "file": f"{tile['output']}/glyph.bmp"
    }

    # Save bitmap
    os.makedirs(tile["output"], exist_ok=True)
    bitmap["image"].save(bitmap["file"])
    return bitmap

def read_provider_bitmap(provider):
    """Reads a provider PNG, composites over black, inverts to black-on-white, and binarizes."""
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
    """Slices each provider's bitmap PNG into individual glyph tiles with pixel and SVG data."""
    log(f"→ ✂️ Slicing bitmap providers into tiles...")

    for provider in providers:
        bitmap = read_provider_bitmap(provider)
        tiles = []

        # Calculate tile dimensions
        width, height = bitmap.size
        glyph_width = width / COLUMNS_PER_ROW

        with tqdm(enumerate(provider["chars"]), total=len(provider["chars"]),
                  desc=f" → 🔣 {provider['file_name']}", unit="tile",
                  ncols=80, leave=False, file=sys.stdout, disable=is_silent()) as tiles_progress:
            for i, unicode in tiles_progress:
                # Skip .notdef
                codepoint = get_unicode_codepoint(unicode)
                if codepoint == 0x0000:
                    continue

                # Update progress bar
                tiles_progress.set_description(f" → 🔣 0x{codepoint:02X}")

                # Collate tile data
                tile_row = i // COLUMNS_PER_ROW
                tile_column = i % COLUMNS_PER_ROW
                tile = {
                    "unicode": unicode,
                    "codepoint": codepoint,
                    "size": (glyph_width, provider.get("height")),
                    "ascent": provider.get("ascent", 0),
                    "location": (tile_column, tile_row),
                    "output": f"{provider['output']}/tiles/{tile_row:02}_{tile_column:02}_{codepoint:04X}"
                }
                tiles.append(tile)

                # Crop tile bitmap from full bitmap
                tile["bitmap"] = crop_tile_from_bitmap(bitmap, tile)

                # Create pixel grid and collect hole data
                tile["pixels"] = convert_tile_into_pixels(tile)

                # Create svg xml and files
                tile["svg"] = convert_tile_into_svg(tile)

        provider["tiles"] = tiles

    total_tiles = sum(len(p["tiles"]) for p in providers)
    log(f" → 🔢 Sliced {total_tiles} glyphs across {len(providers)} providers...")

def read_providers_from_bin(byte_data):
    """Parses legacy binary glyph_sizes.bin format (Minecraft 1.8.9 and earlier).

    Scans for ascii.png (8x8 glyphs) and unicode_page_XX.png (16x16 glyphs)
    in the extracted font textures directory. Creates provider dicts compatible
    with the JSON provider pipeline.
    """
    glyph_widths = list(byte_data)
    providers = []

    glyph_count = sum(1 for w in glyph_widths if w != 0)
    log(f"→ 🛠️ Parsing bitmap providers ({glyph_count} non-empty in glyph_sizes.bin)...")

    # 1. Discover unicode_page_XX.png files (16x16 glyphs, 256 chars per page)
    #    Added first so ascii.png can override codepoints 0-255
    with tqdm(range(256), desc=" → 🔢 Pages", unit="page",
              ncols=80, leave=False, file=sys.stdout, disable=is_silent()) as pages_progress:
        for page in pages_progress:
            page_hex = f"{page:02x}"
            pages_progress.set_description(f" → 🔢 Page {page_hex}")
            page_file = f"unicode_page_{page_hex}.png"
            page_path = f"{TEXTURE_PATH}/{page_file}"

            if not os.path.isfile(page_path):
                continue

            base_cp = page * 256
            chars = []
            for i in range(256):
                cp = base_cp + i
                if cp < len(glyph_widths) and glyph_widths[cp] != 0 and in_unifont_ranges(cp):
                    chars.append(chr(cp))
                else:
                    chars.append(chr(0))

            valid_count = sum(1 for c in chars if c != chr(0))
            if valid_count == 0:
                continue

            name = f"unicode_page_{page_hex}"
            output = f"{WORK_DIR}/glyphs/{name}"
            os.makedirs(output, exist_ok=True)

            providers.append({
                "ascent": 15,
                "height": 16,
                "chars": chars,
                "file_name": page_file,
                "file_path": page_path,
                "name": name,
                "output": output,
                "tiles": []
            })

    unicode_glyph_count = sum(sum(1 for c in p["chars"] if c != chr(0)) for p in providers)
    log(f" → 🔢 Detected {unicode_glyph_count} glyphs across {len(providers)} unicode pages...")

    # 2. ascii.png (8x8 glyphs, codepoints 0-255)
    #    Added last so it takes priority over unicode_page_00 for overlapping codepoints
    name = "ascii"
    ascii_file = f"{name}.png"
    ascii_path = f"{TEXTURE_PATH}/{ascii_file}"

    if os.path.isfile(ascii_path):
        chars = [chr(i) for i in range(256)]
        name = "ascii"
        output = f"{WORK_DIR}/glyphs/{name}"
        os.makedirs(output, exist_ok=True)

        log(f" → 🔢 Detected 256 glyphs in {ascii_file}...")

        providers.append({
            "ascent": 7,
            "height": 8,
            "chars": chars,
            "file_name": ascii_file,
            "file_path": ascii_path,
            "name": name,
            "output": output,
            "tiles": []
        })

    return providers

def read_providers_from_json(byte_data):
    """Parses the JSON font provider format (default.json) into a list of provider dicts."""
    raw_text = byte_data.decode("utf-8", errors="surrogatepass")
    data = parse_json(raw_text)

    log("→ 🛠️ Parsing bitmap providers...")
    providers = []
    for provider in data.get("providers", []):
        if provider.get("type") == "bitmap" and "chars" in provider:
            file_name = provider.get("file", "minecraft:font/").split("minecraft:font/")[-1]
            name = os.path.splitext(file_name)[0]
            output = f"{WORK_DIR}/glyphs/{name}"

            # Create provider directory
            os.makedirs(output, exist_ok=True)

            # Read unicode characters
            chars = [char for row in provider.get("chars", []) for char in row]
            log(f" → 🔢 Detected {len(chars)} unicode characters in '{name}'...")

            providers.append({
                "ascent": provider.get("ascent", 0),
                "height": provider.get("height", DEFAULT_GLYPH_SIZE),
                "chars": chars,
                "file_name": file_name,
                "file_path": f"{MINECRAFT_JAR_DIR}/textures/font/{file_name}",
                "name": name,
                "output": output,
                "tiles": []
            })

    return providers

def read_providers_from_file(file, format):
    """Reads a font provider file, parses it by format, and slices into glyph tiles."""
    log(f"🧩 Parsing {file}...")
    with open(file, "rb") as f:
        raw_bytes = f.read()

    log(f"→ 🛠️ Decoding {format}...")
    if format == "bin":
        providers = read_providers_from_bin(raw_bytes)
    elif format == "json":
        providers = read_providers_from_json(raw_bytes)
    else:
        raise ValueError(f"Unsupported file format: {format}")

    slice_providers_into_tiles(providers)
    return providers

def convert_unifont_to_tiles(unifont_glyphs, bold=False):
    """Converts parsed unifont hex bitmap data into tile dicts with pixel data."""
    tiles = {}
    style_label = "Bold" if bold else "Regular"

    with tqdm(unifont_glyphs.items(), total=len(unifont_glyphs),
              desc=f" → 🔣 {style_label}", unit="glyph",
              ncols=80, leave=False, file=sys.stdout, disable=is_silent()) as progress:
        for codepoint, bitmap_rows in progress:
            bitmap_grid = np.array(bitmap_rows, dtype=np.uint8)
            pixel_data = _bitmap_to_pixel_data(bitmap_grid, bold)
            width = len(bitmap_rows[0]) if bitmap_rows else 8

            svg = None
            if UNIFONT_DEBUG_SVG:
                output = f"{WORK_DIR}/glyphs/unifont/{style_label.lower()}/{codepoint:04X}"
                os.makedirs(output, exist_ok=True)
                svg = _write_tile_svg(pixel_data["grid"], (width, 16), f"{output}/{style_label.lower()}.svg")

            tiles[codepoint] = {
                "unicode": chr(codepoint),
                "codepoint": codepoint,
                "size": (width, 16),
                "ascent": 15,
                "pixels": pixel_data,
                "svg": svg,
                "source": "unifont"
            }

    return tiles

def precompute_glyph_scaling(glyph_map):
    """Pre-computes base scaled coordinates (pixel space to font units) for all glyphs."""
    styles = len(glyph_map)
    per_style = len(next(iter(glyph_map.values())))
    total = per_style * styles
    log(f"→ ✖️ Pre-scaling {per_style} glyphs ({styles} styles)...")

    with tqdm(total=total, desc=" → 🔣 Scaling", unit="glyph",
              ncols=80, leave=False, file=sys.stdout, disable=is_silent()) as progress:
        for style_key in glyph_map:
            for cp, tile in glyph_map[style_key].items():
                progress.update(1)
                pixels = tile.get("pixels")
                if not pixels:
                    tile["scaled"] = {"outer": [], "holes": []}
                    continue

                paths = pixels.get("paths", {})
                holes = pixels.get("holes", {})

                outer_paths = [p["corners"] for p in paths.values() if len(p.get("corners", [])) >= 3]
                hole_paths = [h["corners"] for h in holes.values() if len(h.get("corners", [])) >= 3]

                all_points = [pt for path in outer_paths + hole_paths for pt in path]
                if not all_points:
                    tile["scaled"] = {"outer": [], "holes": []}
                    continue

                min_x = min(x for x, y in all_points)
                width, height = tile["size"]
                scale_x = UNITS_PER_EM / width
                scale_y = UNITS_PER_EM / height
                descender_offset = height - 1

                def transform(pt, _min_x=min_x, _sx=scale_x, _sy=scale_y, _do=descender_offset):
                    x, y = pt
                    return ((x - _min_x) * _sx, (_do - y) * _sy)

                tile["scaled"] = {
                    "outer": [[transform(pt) for pt in path] for path in outer_paths],
                    "holes": [[transform(pt) for pt in path] for path in hole_paths]
                }

def build_glyph_map(providers, unifont_glyphs):
    """Builds a unified glyph map merging provider glyphs (priority) with unifont fallbacks."""
    log(f"🧩 Building unified glyph map...")
    glyph_map = {"Regular": OrderedDict(), "Bold": OrderedDict()}

    # 1. Add provider glyphs (priority - added first)
    for provider in providers:
        for tile in provider["tiles"]:
            cp = tile["codepoint"]
            for style_key in ("Regular", "Bold"):
                style = style_key.lower()
                flat_tile = {
                    "unicode": tile["unicode"],
                    "codepoint": cp,
                    "size": tile["size"],
                    "ascent": tile["ascent"],
                    "pixels": tile["pixels"][style],
                    "svg": tile["svg"][style] if tile.get("svg") else None,
                    "source": "provider"
                }
                glyph_map[style_key][cp] = flat_tile

    provider_count = len(glyph_map["Regular"])
    log(f"→ 🔣 {provider_count} provider glyphs (priority)")

    # 2. Add unifont glyphs (fallback - skip if codepoint exists)
    if unifont_glyphs:
        log(f"→ 🔣 Processing unifont fallback glyphs...")
        for style_key, bold in [("Regular", False), ("Bold", True)]:
            unifont_tiles = convert_unifont_to_tiles(unifont_glyphs, bold)
            for cp, tile in unifont_tiles.items():
                if cp not in glyph_map[style_key]:
                    glyph_map[style_key][cp] = tile

    # 3. Sort by codepoint
    for key in glyph_map:
        glyph_map[key] = OrderedDict(sorted(glyph_map[key].items()))

    # 4. Print summary
    unifont_count = sum(1 for t in glyph_map["Regular"].values() if t["source"] == "unifont")
    total = len(glyph_map["Regular"])
    log(f"→ 🔢 Prepared {total} glyphs ({provider_count} provider, {unifont_count} unifont)")

    # 5. Pre-compute scaling
    precompute_glyph_scaling(glyph_map)

    return glyph_map

def clean_directories(output_dir=None):
    """Removes and recreates the work/ and output/ directories."""
    if output_dir is None:
        output_dir = OUTPUT_DIR

    log("🧹 Cleaning work directory...")
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    os.makedirs(WORK_DIR, exist_ok=True)

    log("🧹 Cleaning output directory...")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)
