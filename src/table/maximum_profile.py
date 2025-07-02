from fontTools.ttLib import newTable

from src.util.constants import BITMAP_GLYPH_SIZE

def create_font_mprofile_table(font, use_cff: bool = True):
    print("→ 📄 Generating maximum profile table...")
    maxp = font["maxp"] = newTable("maxp")
    maxp.tableVersion = 0x00005000 if use_cff else 0x00010000
    maxp.maxPoints = BITMAP_GLYPH_SIZE * BITMAP_GLYPH_SIZE
