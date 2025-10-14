import sys

from fontTools.ttLib import TTFont
from tqdm import tqdm

from src.glyph.glyph_storage import GlyphStorage
from src.table.glyph_mappings import create_font_mapping_table
from src.table.header import create_font_header_table
from src.table.horizontal_header import create_font_hheader_table
from src.table.horizontal_metrics import create_font_hmetrics_table
from src.table.maximum_profile import create_font_mprofile_table
from src.table.name import create_font_name_table
from src.table.opentype import create_ot_font_tables
from src.table.os2_metrics import create_font_metrics_table
from src.table.postscript import create_font_pscript_table
from src.table.truetype import create_tt_font_tables

def convert_unicode_to_glyphs(providers, glyph_storage):
    total_tiles = sum(len(provider["tiles"]) for provider in providers)
    print(f"→ 🔣 Converting {total_tiles} unicode to glyphs...")

    for provider in providers:
        with tqdm(provider["tiles"], total=len(provider["chars"]),
                  desc=" → 🔣 Tiles", unit="tile",
                  ncols=80, leave=False, file=sys.stdout) as tiles_progress:
            for tile in tiles_progress:
                # Create new glyph
                glyph = glyph_storage.new_glyph(tile)

                # Skip invalid and .notdef characters
                if not glyph.valid():
                    continue

                # Export svg path
                glyph.write_svg_paths()

                # Scale svg
                glyph.scale()

                # Draw svg
                glyph.draw()

                # Save glyph
                glyph_storage.add(glyph)

def create_font_file(providers, use_cff: bool = True, bold: bool = False, italic: bool = False):
    font_icon = "🅾️" if use_cff else "🆎"
    font_type = "OpenType" if use_cff else "TrueType"
    print(f"{font_icon} Creating {font_type} font file...")

    # Create font tables
    font = TTFont()
    create_font_header_table(font, use_cff)
    create_font_hheader_table(font, use_cff)
    create_font_mprofile_table(font, use_cff)
    create_font_pscript_table(font, use_cff)
    create_font_hmetrics_table(font)
    create_font_name_table(font)
    create_font_metrics_table(font)
    create_font_mapping_table(font)

    if use_cff:
        create_ot_font_tables(font, bold, italic)
    else:
        create_tt_font_tables(font)

    # bold font: offset to the right on the x-axis by 1 pixel
    # italic font: shearing (slant) transformation: X-axis shear
    # every row of pixels is shifted right by a small offset based on its vertical position
    # shear factor: 0.2
    # shear angle: 11.3099325 deg / 0.19739556 rad / atan(0.2)

    # Create glyph storage
    glyph_storage = GlyphStorage(font, use_cff)

    # Convert unicode to glyphs
    convert_unicode_to_glyphs(providers, glyph_storage)

    # Add .notdef
    glyph_storage.add_notdef()

    # Write glyphs
    glyph_storage.write()

    return glyph_storage
