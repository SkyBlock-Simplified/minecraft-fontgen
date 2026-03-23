from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

def create_font_mapping_table(font):
    """Creates the 'cmap' table with BMP (Format 4) and SMP (Format 12) subtables."""
    cmap = font["cmap"] = newTable("cmap")
    cmap.tableVersion = 0
    cmap.tables = []

    def new_table(format, platform, encoding):
        table = CmapSubtable.newSubtable(format)
        table.platformID = platform # Windows = 3
        table.platEncID = encoding # Unicode UCS (BMP = UCS-2, SMP = UCS-4)
        table.language = 0
        table.cmap = {}
        return table

    cmap.tables.append(new_table(4, 3, 1)) # BMP (Format 4) (U+0000 - U+FFFF)
    cmap.tables.append(new_table(12, 3, 10)) # SMP (Format 12) (U+10000 - U+1FFFF)
