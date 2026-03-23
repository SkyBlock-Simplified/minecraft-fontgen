import sys

from fontTools.ttLib import TTFont
from tqdm import tqdm

from minecraft_fontgen.functions import log, is_silent

from minecraft_fontgen.glyph.glyph_storage import GlyphStorage
from minecraft_fontgen.table.glyph_mappings import create_font_mapping_table
from minecraft_fontgen.table.header import create_font_header_table
from minecraft_fontgen.table.horizontal_header import create_font_hheader_table
from minecraft_fontgen.table.horizontal_metrics import create_font_hmetrics_table
from minecraft_fontgen.table.maximum_profile import create_font_mprofile_table
from minecraft_fontgen.table.name import create_font_name_table
from minecraft_fontgen.table.opentype import create_ot_font_tables
from minecraft_fontgen.table.os2_metrics import create_font_metrics_table
from minecraft_fontgen.table.postscript import create_font_pscript_table
from minecraft_fontgen.table.truetype import create_tt_font_tables

def create_font_files(glyph_map, use_cff, output_fonts, output_dir, output_font_name, output_file_ext):
    """Creates all enabled font files in batch: initializes tables, converts glyphs, saves. Returns output file paths."""
    font_icon = "🅾️" if use_cff else "🆎"
    font_type = "OpenType" if use_cff else "TrueType"
    enabled_fonts = [(name, bold, italic) for name, enabled, bold, italic in output_fonts if enabled]

    if not enabled_fonts:
        log("→ ⚠️ No font styles enabled.")
        return []

    log(f"{font_icon} Creating {font_type} font files...")

    # Initialize font tables and glyph storages for each style
    storages = {}
    for font_name, is_bold, is_italic in enabled_fonts:
        log(f"→ 📄 Initializing {font_name.lower()} tables...")
        font = TTFont()
        create_font_header_table(font, use_cff)
        create_font_hheader_table(font, use_cff)
        create_font_mprofile_table(font, use_cff)
        create_font_pscript_table(font, use_cff)
        create_font_hmetrics_table(font)
        create_font_name_table(font, is_bold, is_italic)
        create_font_metrics_table(font)
        create_font_mapping_table(font)

        if use_cff:
            create_ot_font_tables(font, is_bold, is_italic)
        else:
            create_tt_font_tables(font)

        storages[font_name] = (GlyphStorage(font, use_cff), is_bold, is_italic)

    # Convert glyphs for all styles in a single pass
    tiles_per_style = len(glyph_map["Regular"])
    total = tiles_per_style * len(enabled_fonts)
    log(f"→ 🔣 Converting {tiles_per_style} glyphs ({len(enabled_fonts)} styles)...")

    with tqdm(total=total, desc=f" → 🔣 {enabled_fonts[0][0]}", unit="glyph",
              ncols=80, leave=False, file=sys.stdout, disable=is_silent()) as progress:
        for font_name, is_bold, is_italic in enabled_fonts:
            progress.set_description(f" → 🔣 {font_name}")
            pixel_style = "Bold" if is_bold else "Regular"
            tiles = glyph_map[pixel_style]
            storage = storages[font_name][0]

            for tile in tiles.values():
                progress.update(1)
                glyph = storage.new_glyph(tile)

                if not glyph.valid():
                    continue

                if tile.get("svg") and not is_italic:
                    glyph.write_svg_paths()

                glyph.scale(italic=is_italic)
                glyph.draw()
                storage.add(glyph)

    # Finalize and save all fonts
    log(f"→ 💾 Saving font files...", flush=True)
    output_files = []
    for font_style, (storage, _, _) in storages.items():
        output_file = f"{output_font_name}-{font_style}.{output_file_ext}"
        output_path = f"{output_dir}/{output_file}"
        log(f" → ☕ {output_file}...", flush=True)
        storage.add_notdef()
        storage.write()
        storage.save(output_path)
        output_files.append(output_path)

    return output_files
