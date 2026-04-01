from math import atan

# =============================
# === RUNTIME CONFIGURATION ===
# =============================

SILENT_LOG = False # True to disable logging
OUTPUT_DIR = "output"
OPENTYPE = True # False for TrueType

# ==================================
# === FONT DETAILS / DO NOT EDIT ===
# ==================================

VERSION = "1.1.0"
MANUFACTURER = "SkyBlock Simplified"
DESIGNER = "CraftedFury"
COPYRIGHT = "Copyright © Mojang AB"
TRADEMARK = "The glyphs used in this font file are trademarked by Mojang."
VENDOR_URL = "https://github.com/SkyBlock-Simplified/minecraft-fontgen"
DESIGNER_URL = "https://sbs.dev/"
LICENSE_TEXT = "The glyphs used in this font file are licensed by Mojang."
DESCRIPTION = "Build your own font files containing the Minecraft font glyphs."
SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog. 0123456789"

# ===============================
# === CONSTANTS / DO NOT EDIT ===
# ===============================

# File Output
OUTPUT_FONT_NAME = "Minecraft"

# File Input
WORK_DIR = "work"
MINECRAFT_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
MINECRAFT_RESOURCE_URL = "https://resources.download.minecraft.net"
MINECRAFT_JAR_DIR = WORK_DIR + "/assets/minecraft"
MINECRAFT_BIN_FILE = f"{MINECRAFT_JAR_DIR}/font/glyph_sizes.bin"
MINECRAFT_JSON_FILE = f"{MINECRAFT_JAR_DIR}/font/include/default.json"
UNIFONT_PATH = "minecraft/font/include/unifont.json"
TEXTURE_PATH = f"{MINECRAFT_JAR_DIR}/textures/font"
VALIDATE_SCRIPT = "validate_font.py"

# Font Styles (toggle "enabled" to include/exclude a style)
FONT_STYLES = [
    {
        "name": "Regular",
        "enabled": True,
        "bold": False,
        "italic": False,
        "pixel_style": "Regular",
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
    {
        "name": "Bold",
        "enabled": True,
        "bold": True,
        "italic": False,
        "pixel_style": "Bold",
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
    {
        "name": "Italic",
        "enabled": True,
        "bold": False,
        "italic": True,
        "pixel_style": "Regular",
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
    {
        "name": "BoldItalic",
        "enabled": True,
        "bold": True,
        "italic": True,
        "pixel_style": "Bold",
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
    {
        "name": "Galactic",
        "enabled": True,
        "bold": False,
        "italic": False,
        "pixel_style": "Galactic",
        "json_file": f"{MINECRAFT_JAR_DIR}/font/alt.json",
        "map_lowercase": True,  # Duplicate uppercase glyphs onto lowercase codepoints
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
    {
        "name": "Illageralt",
        "enabled": True,
        "bold": False,
        "italic": False,
        "pixel_style": "Illageralt",
        "json_file": f"{MINECRAFT_JAR_DIR}/font/illageralt.json",
        "map_lowercase": False,
        "debug": {
            "svg": False,
            "bmp": False,
            "unifont": False
        },
    },
]

# FontTools Epoch
MAC_EPOCH = 2082844800 # Seconds since 12:00 midnight, January 1, 1904 UTC

# Glyph
COLUMNS_PER_ROW = 16
DEFAULT_GLYPH_SIZE = 8
UNITS_PER_EM = 1024
ASCENT = (DEFAULT_GLYPH_SIZE - 1) * (UNITS_PER_EM // DEFAULT_GLYPH_SIZE)  # 7 * 128 = 896
DESCENT = -(UNITS_PER_EM // DEFAULT_GLYPH_SIZE)  # -128
BOUNDING_BOX = [0, -256, 1280, 1280]
MAX_ADVANCE_WIDTH = BOUNDING_BOX[2] + BOUNDING_BOX[1]
NOTDEF = ".notdef"
NOTDEF_GLYPH = [
    [20, 0, 437, 675], # Inner rectangle
    [68, 48, 388, 627] # Outer rectangle
]

# Italic Glyph
ITALIC_SHEAR_VERTICAL = 5
ITALIC_SHEAR_FACTOR = 1 / ITALIC_SHEAR_VERTICAL
ITALIC_SHEAR_ANGLE = atan(ITALIC_SHEAR_FACTOR)

# Unifont Codepoint Ranges
# Only include these Unicode ranges from unifont hex files.
# Provider glyphs (from Minecraft bitmap PNGs) are always included regardless.
UNIFONT_RANGES = [
    (0x0000, 0x052F),   # Basic Latin through Cyrillic Supplement
    (0x0530, 0x058F),   # Armenian
    (0x0590, 0x05FF),   # Hebrew
    (0x0600, 0x06FF),   # Arabic
    (0x0700, 0x074F),   # Syriac
    (0x0750, 0x077F),   # Arabic Supplement
    (0x0780, 0x07BF),   # Thaana
    (0x07C0, 0x07FF),   # NKo
    (0x0E00, 0x0E7F),   # Thai
    (0x10A0, 0x10FF),   # Georgian
    (0x1100, 0x11FF),   # Hangul Jamo
    (0x1D00, 0x1DFF),   # Phonetic Extensions + Supplement + Combining Marks Supp
    (0x1E00, 0x1FFF),   # Latin Extended Additional + Greek Extended
    (0x2000, 0x2BFF),   # General Punctuation through Misc Symbols and Arrows
    (0x2C00, 0x2C7F),   # Glagolitic + Latin Extended-C
    (0x2C80, 0x2CFF),   # Coptic
    (0x2E00, 0x2E7F),   # Supplemental Punctuation
    (0xA720, 0xA7FF),   # Latin Extended-D
    (0xAB30, 0xAB6F),   # Latin Extended-E
    (0xFB00, 0xFB06),   # Latin ligatures (Alphabetic Presentation Forms)
    (0xFE20, 0xFE2F),   # Combining Half Marks
    (0xFE50, 0xFE6F),   # Small Form Variants
    (0xFF01, 0xFF5E),   # Fullwidth ASCII
    (0xFFF0, 0xFFFD),   # Specials
]
