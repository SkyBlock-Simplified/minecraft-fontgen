from fontTools.ttLib import newTable

from src.util.constants import DEFAULT_GLYPH_SIZE

def create_font_mprofile_table(font, use_cff: bool = True):
    print("→ 📄 Generating maximum profile table...")
    maxp = font["maxp"] = newTable("maxp")
    maxp.tableVersion = 0x00005000 if use_cff else 0x00010000
    maxp.maxPoints = DEFAULT_GLYPH_SIZE * DEFAULT_GLYPH_SIZE
