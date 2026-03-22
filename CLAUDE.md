# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Minecraft-FontGen converts Minecraft's bitmap font glyphs into OpenType (CFF) or TrueType font files. It downloads a selected Minecraft version's JAR via the Piston API, extracts bitmap PNG textures and font provider JSON, then traces pixel contours into vector outlines and assembles complete `.otf`/`.ttf` fonts using fontTools.

## Commands

```bash
# Activate venv
.venv/Scripts/activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Run the tool (interactive - prompts for Minecraft version)
python -m src.main

# Validate output with FontForge (requires fontforge installed)
fontforge -lang=py -script src/inspect/validate.py output/Minecraft-Regular.otf
```

There are no tests or linting configured.

## Architecture

### Pipeline (src/main.py)

The pipeline runs sequentially through five stages:

1. **Clean** (`src/file_io.py:clean_directories`) - Wipes and recreates `work/` and `output/` directories
2. **Download** (`src/piston.py:read_minecraft_piston_api`) - User selects a Minecraft version interactively. Downloads version manifest, client JAR, and extracts font assets to `work/`. Then downloads unifont hex files if enabled. Returns the matched font file path, format, and unifont glyph data
3. **Parse + Slice** (`src/file_io.py:read_providers_from_file`) - Reads `include/default.json` from the extracted JAR to discover bitmap font providers (PNG files + Unicode character mappings). Internally calls `slice_providers_into_tiles` to crop individual glyphs from bitmap PNGs, build pixel grids with flood-fill contour tracing, and generate SVG debug output
4. **Build glyph map** (`src/file_io.py:build_glyph_map`) - Merges provider glyphs (priority) with unifont fallback glyphs into an `OrderedDict` keyed by codepoint, per style (Regular/Bold). Pre-computes scaled coordinates (pixel space to font units) for all glyphs via `precompute_glyph_scaling`
5. **Create font files** (`src/font_creator.py:create_font_files`) - Batch creates all enabled font styles (Regular, Bold, Italic, BoldItalic). Initializes fontTools `TTFont` tables for each style, converts glyphs with a single progress bar across all styles, then finalizes and saves all fonts

### Glyph Processing

- `src/file_io.py:_bitmap_to_pixel_data` - Core contour tracing: flood-fill labels pixel groups, traces boundary edges using right-hand rule, extracts corner points for vector outlines. Bold glyphs get a 1px rightward expansion before tracing
- `src/file_io.py:precompute_glyph_scaling` - Pre-computes base scaled coordinates (pixel space to font units) for all glyphs during glyph map building. This is style-independent; only italic shear differs and is applied as a lightweight post-transform per font
- `src/glyph/glyph.py:Glyph` - Assigns pre-computed scaled coordinates, applies italic shear transform if needed, draws via fontTools pen (T2CharStringPen for CFF, TTGlyphPen for TrueType)
- `src/glyph/glyph_storage.py:GlyphStorage` - Accumulates glyphs, manages cmap table entries (Format 4 for BMP, Format 12 for SMP), writes final glyph order and metrics

### Font Table Modules (src/table/)

Each file creates one OpenType/TrueType table via `fontTools.ttLib.newTable()`. They set initial values; `GlyphStorage.write()` patches final glyph-dependent values (numGlyphs, charIndex ranges, average widths, etc.) after all glyphs are added.

- `header.py` - `head` table (timestamps, bounding box, unitsPerEm)
- `horizontal_header.py` - `hhea` table (ascent, descent, line gap)
- `maximum_profile.py` - `maxp` table (glyph count placeholder)
- `postscript.py` - `post` table (italic angle, underline, fixed pitch)
- `horizontal_metrics.py` - `hmtx` table (advance widths, LSBs)
- `name.py` - `name` table (family, style, version, metadata strings)
- `os2_metrics.py` - `OS/2` table (weight class, panose, unicode ranges)
- `glyph_mappings.py` - `cmap` table (Format 4 for BMP, Format 12 for SMP)
- `opentype.py` - CFF tables (font set, top dict, charstrings)
- `truetype.py` - TrueType tables (glyf, loca)

### Key Constants (src/config.py)

Configuration is module-level constants, not CLI args. Key settings:
- `OPENTYPE = True` - CFF (OpenType) vs TrueType outlines
- `UNIFONT = True` - Include GNU Unifont fallback glyphs
- `CREATE_REGULAR/BOLD/ITALIC` - Which font styles to generate
- `UNITS_PER_EM = 1024`, `DEFAULT_GLYPH_SIZE = 8` - Font metrics
- `BOUNDING_BOX = [0, -128, 1152, 896]` - Global glyph bounds
- `OUTPUT_FONT_NAME = "Minecraft"` - Output font family name
- `OUTPUT_FONTS` - List of `(name, enabled, bold, italic)` tuples for all four styles

### Batch Font Creation

All enabled font styles are created in a single batch call (`create_font_files`). The process:
1. Initialize `TTFont` + `GlyphStorage` for each enabled style
2. Single `tqdm` progress bar iterates all styles, showing the current style name
3. For each glyph: create from tile, validate, apply pre-computed scaling (with italic shear if needed), draw, and add to storage
4. Finalize all fonts (add .notdef, write glyph order/metrics) and save

Pens are per-font (CFF T2CharString or TT glyph), so glyph objects cannot be shared between styles. However, the pre-computed scaling coordinates are shared since they are style-independent.

### Italic Handling

Italic and BoldItalic reuse Regular/Bold pixel data respectively. The italic shear is applied during `Glyph.scale()` by adding `sy * ITALIC_SHEAR_FACTOR` to x-coordinates of the pre-computed base coordinates.

### Unifont Fallback

When `UNIFONT = True`, GNU Unifont hex files are downloaded from Minecraft's asset index and parsed into 16-row bitmap grids (`src/piston.py:parse_unifont_hex_bytes`). These are converted to tile dicts via `convert_unifont_to_tiles` and merged as fallbacks (lower priority than provider glyphs) in `build_glyph_map`. The `UNIFONT_RANGES` config controls which Unicode ranges are included.

### Directory Layout at Runtime

- `work/` - Downloaded JAR, extracted assets, sliced tile bitmaps + debug SVGs (gitignored)
- `output/` - Generated `.otf`/`.ttf` files (gitignored)
- `src/font/` - Reference copies of Minecraft's font provider JSONs

## Dependencies

fontTools (font building), Pillow (bitmap processing), numpy (pixel grid operations), requests (Mojang API downloads), tqdm (progress bars), svgpathtools/uharfbuzz (SVG utilities). Python 3.7+.

## Module Import Style

Source files use absolute imports from `src` (e.g., `from src.config import ...`). There are no `__init__.py` files; the project runs as `python -m src.main`.
