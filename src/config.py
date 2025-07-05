from math import atan

# Font
AUTHOR = "CraftedFury"
FONT_NAME = "Minecraft"
VERSION = "1.1.0"
MAC_EPOCH = 2082844800 # FontTools requires seconds since 12:00 midnight, January 1, 1904 UTC
OPENTYPE = True # False for TrueType
CREATE_BMP = True # BMP (Format 4) (U+0000 - U+FFFF)
CREATE_SMP = True # SMP (Format 12) (U+10000 - U+1FFFF)

# === CONSTANTS / DO NOT EDIT ===

# File Input/Output
OUTPUT_DIR = "output"
OUTPUT_FONT_FILE = f"{OUTPUT_DIR}/{FONT_NAME}" + (".otf" if OPENTYPE else ".ttf")
MOJANG_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
MINECRAFT_JAR_DIR = OUTPUT_DIR + "/assets/minecraft"

# Glyph
COLUMNS_PER_ROW = 16
DEFAULT_GLYPH_SIZE = 8
BOUNDING_BOX = [0, -128, 1152, 896]
UNITS_PER_EM = 1024
ASCENT = BOUNDING_BOX[3]
DESCENT = BOUNDING_BOX[1]
ADVANCE_WIDTH = BOUNDING_BOX[2] + BOUNDING_BOX[1]
NOTDEF = ".notdef"
NOTDEF_GLYPH = [20, 0, 437, 675]

# Italic Glyph
ITALIC_SHEAR_VERTICAL = 5
ITALIC_SHEAR_FACTOR = 1 / ITALIC_SHEAR_VERTICAL
ITALIC_SHEAR_ANGLE = atan(ITALIC_SHEAR_FACTOR)
