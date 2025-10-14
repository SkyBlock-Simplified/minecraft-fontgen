import time

from fontTools.ttLib import newTable
from src.config import UNITS_PER_EM, BOUNDING_BOX, DEFAULT_GLYPH_SIZE, MAC_EPOCH

def create_font_header_table(font, use_cff: bool = True):
    print("→ 📄 Generating header table...")
    now = int(time.time())
    head = font["head"] = newTable("head")
    head.checkSumAdjustment = 0 # Used to ensure the font has a valid file checksum (recalculated automatically)
    head.created = now + (MAC_EPOCH - int(time.mktime(time.gmtime(0)))) # Creation timestamp of the font (unix timestamp)
    head.flags = 11 # Bit flags that define font-wide behavior (e.g., baseline, left sidebearing point at x=0)
    head.fontRevision = 1.0
    head.fontDirectionHint = 2 # Used by font renderers for direction hints (usually set to 2 for modern fonts)
    head.glyphDataFormat = 0
    head.indexToLocFormat = 1 if not use_cff else 0 # 0 = short offsets (16-bit), 1 = long offsets (32-bit) in the loca table
    head.lowestRecPPEM = DEFAULT_GLYPH_SIZE # Smallest readable pixel size the font is designed for (in pixels per em)
    head.macStyle = 0 # Bit flags for font styling (e.g., bold, italic)
    head.magicNumber = 0x5F0F3CF5 # Verification signature for OpenType and TrueType
    head.modified = now + (MAC_EPOCH - int(time.mktime(time.gmtime(0)))) # Last modified timestamp of the font
    head.tableVersion = 0x00005000 if use_cff else 0x00001000
    head.unitsPerEm = UNITS_PER_EM # Defines the em square size (Higher values increase the resolution of glyph coordinates)
    head.xMin, head.yMin, head.xMax, head.yMax = BOUNDING_BOX # Bounding Box of all glyphs
