from fontTools.ttLib import newTable
from fontTools.ttLib.tables.O_S_2f_2 import Panose

from src.config import ASCENT, DESCENT

def create_font_metrics_table(font):
    print("→ 📄 Generating metrics table...")
    os2 = font["OS/2"] = newTable("OS/2")
    os2.achVendID = "PYFT" # 4-character identifier for the vendor (e.g., PYFT, NONE)
    os2.fsSelection = 0x0040 # Bit flags for styling (e.g., italic, bold)
    os2.fsType = 0 # Embedding permissions for digital rights
    os2.panose = [0] * 10 # 10-byte classification vector for font matcher algorithms (0 for unspecified)

    os2.panose = Panose()
    os2.panose.bArmStyle = 0
    os2.panose.bContrast = 0
    os2.panose.bFamilyType = 0
    os2.panose.bLetterForm = 0
    os2.panose.bMidline = 0
    os2.panose.bProportion = 0
    os2.panose.bSerifStyle = 0
    os2.panose.bStrokeVariation = 0
    os2.panose.bWeight = 0
    os2.panose.bXHeight = 0

    os2.sCapHeight = int(ASCENT * 0.7) # Typically 70% of ascent
    os2.sFamilyClass = 0 # Font family group classification (0 for no classification)
    os2.sTypoAscender = ASCENT # Preferred ascent for line layout
    os2.sTypoDescender = DESCENT # Preferred descent for line layout
    os2.sTypoLineGap = 0 # Preferred line gap for layout
    os2.sxHeight = int(ASCENT * 0.46) # Typically 46% of ascent
    os2.ulCodePageRange1 = 0xFFFFFFFF # Bits indicating which Windows code pages are supported
    os2.ulCodePageRange2 = 0xFFFFFFFF # Bits indicating which Windows code pages are supported
    os2.ulUnicodeRange1 = 0xFFFFFFFF # Bits indicating which Unicode blocks are supported
    os2.ulUnicodeRange2 = 0xFFFFFFFF # Bits indicating which Unicode blocks are supported
    os2.ulUnicodeRange3 = 0xFFFFFFFF # Bits indicating which Unicode blocks are supported
    os2.ulUnicodeRange4 = 0xFFFFFFFF # Bits indicating which Unicode blocks are supported
    os2.usBreakChar = 32 # Usually space
    os2.usDefaultChar = 0 # Usually 0
    os2.usMaxContext = 2 # Minimal context (tune if required)
    os2.usWeightClass = 400 # Weight of the font (e.g., 400 = normal, 700 = bold)
    os2.usWidthClass = 5 # Width of the font (1 = ultra-condensed, 10 = ultra-expanded, 5 = normal)
    os2.usWinAscent = ASCENT # Used by Windows for clipping
    os2.usWinDescent = abs(DESCENT) # Used by Windows for clipping
    os2.version = 4
    os2.yStrikeoutPosition = 250 # Vertical position of the strikeout line
    os2.yStrikeoutSize = 50 # Thickness of the strikeout line
    os2.ySubscriptXOffset = 0 # Horizontal offset for subscript
    os2.ySubscriptXSize = 650 # Subscript character width
    os2.ySubscriptYOffset = 75 # Vertical offset for subscript
    os2.ySubscriptYSize = 600 # Subscript character height
    os2.ySuperscriptXOffset = 0 # Horizontal offset for superscript
    os2.ySuperscriptXSize = 650 # Superscript character width
    os2.ySuperscriptYOffset = 350 # Vertical offset for superscript
    os2.ySuperscriptYSize = 600 # Superscript character height
    os2.xAvgCharWidth = 512 # Average character width (mean of the advanced widths)
