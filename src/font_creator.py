from fontTools.ttLib import TTFont

from src.classes.glyph_storage import GlyphStorage
from src.classes.svg import Svg
from src.classes.unicode_char import UnicodeChar
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
from src.util.functions import progress_bar

def convert_unicode_to_glyphs(providers, glyph_storage):
    total_chars = sum(len(provider["chars"]) for provider in providers)
    print(f"→ 🔣 Converting {total_chars} unicode to glyphs...")
    index = 0

    for provider in providers:
        for unicode_char, svg_file in zip(provider["chars"], provider["svg_files"]):
            # Show progress bar
            progress_bar(index, total_chars)
            index += 1

            # Load unicode
            unicode = UnicodeChar(unicode_char)

            # Skip invalid and .notdef characters
            if unicode.codepoint is None:
                print(f" → ⚠️ Skipping invalid unicode '0x{unicode.codepoint:04X}'.")
                continue
            elif unicode.codepoint == 0x0000:
                continue

            # Load svg file and path
            svg = Svg(svg_file)
            svg.read_path()

            # Adjust scaling and positioning
            svg_path = svg.scale(provider["glyph_height"])

            # Draw svg path
            pen = glyph_storage.draw(svg_path)

            # Save glyph
            glyph_storage.add(unicode, pen)

    # Finish the progress bar
    progress_bar(total_chars, total_chars)
    print()

def create_font_file(providers, use_cff: bool = True):
    font_icon = "🅾️" if use_cff else "🆎"
    font_type = "OpenType" if use_cff else "TrueType"
    print(f"{font_icon} Creating {font_type} font file...")

    # Create font tables
    font = TTFont()
    create_font_header_table(font, use_cff)
    create_font_hheader_table(font, use_cff)
    create_font_mprofile_table(font, use_cff)
    create_font_hmetrics_table(font)
    create_font_name_table(font)
    create_font_metrics_table(font)
    create_font_pscript_table(font, use_cff)
    create_font_mapping_table(font)

    if use_cff:
        create_ot_font_tables(font)
    else:
        create_tt_font_tables(font)

    # bold font: offset to the right on the x-axis by 1 pixel
    # italic font: shearing (slant) transformation: X-axis shear
    # every row of pixels is shifted right by a small offset based on its vertical position
    # shear factor: 0.2
    # shear angle: 11.31: atan(0.2)

    # Create glyph storage
    glyph_storage = GlyphStorage(font, use_cff)

    # Convert unicode to glyphs
    convert_unicode_to_glyphs(providers, glyph_storage)

    # Sort glyphs
    glyph_storage.sort()

    # Write glyphs
    glyph_storage.write()

    return glyph_storage
