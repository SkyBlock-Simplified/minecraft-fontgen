from fontTools.ttLib import newTable

from src.util.constants import (
    ASCENT, DESCENT, ADVANCE_WIDTH, BOUNDING_BOX
)

def create_font_hheader_table(font, use_cff: bool = True):
    print("→ 📄 Generating horizontal header table...")
    hhea = font["hhea"] = newTable("hhea")
    hhea.advanceWidthMax = ADVANCE_WIDTH # Maximum advance width among all glyphs
    #hhea.ascender = ASCENT
    hhea.ascent = ASCENT # Used for line height and vertical alignment
    hhea.caretOffset = 0
    hhea.caretSlopeRise = 1 # Defines the slope of the caret for italic text
    hhea.caretSlopeRun = 0 # Defines the slope of the caret for italic text
    #hhea.descender = DESCENT
    hhea.descent = DESCENT # Depth below baseline (negative value)
    hhea.lineGap = 0 # Extra space between lines
    hhea.metricDataFormat = 0 # Reserved (should be 0)
    hhea.minLeftSideBearing = 0 # Smallest left sidebearing of any glyph
    hhea.minRightSideBearing = BOUNDING_BOX[1] # Smallest right sidebearing of any glyph
    hhea.reserved0 = 0
    hhea.reserved1 = 0
    hhea.reserved2 = 0
    hhea.reserved3 = 0
    hhea.tableVersion = 0x50000000 if use_cff else 0x00010000
    hhea.xMaxExtent = BOUNDING_BOX[2] # Maximum horizontal extent (left sidebearing + glyph width)
