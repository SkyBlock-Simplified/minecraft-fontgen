from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from src.util.config import CREATE_SMP, CREATE_BMP


def create_font_mapping_table(font):
    print("→ 📄 Generating glyph mappings...")
    cmap = font["cmap"] = newTable("cmap")
    cmap.tableVersion = 0
    cmap.tables = []

    if CREATE_BMP:
        print(" → ➕ Adding basic multilingual plane support (U+0000 - U+FFFF)...")
        cmap4 = CmapSubtable.newSubtable(4)
        cmap4.platformID = 3 # Windows
        cmap4.platEncID = 1 # Unicode BMP (UCS-2)
        cmap4.language = 0
        cmap4.cmap = {}
        cmap.tables.append(cmap4)

    if CREATE_SMP:
        print(" → ➕ Adding supplementary multilingual plane support (U+0000 - U+10FFFF)...")
        cmap12 = CmapSubtable.newSubtable(12)
        cmap12.platformID = 3 # Windows
        cmap12.platEncID = 10 # Unicode SMP (UCS-4)
        cmap12.language = 0
        cmap12.cmap = {}
        cmap.tables.append(cmap12)

    if len(cmap.tables) == 0:
        raise ValueError("You need at least 1 subtable type enabled.")
