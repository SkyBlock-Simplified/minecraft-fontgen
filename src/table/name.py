from fontTools.ttLib import newTable
from fontTools.ttLib.tables._n_a_m_e import makeName

from src.config import FONT_NAME, VERSION

def create_font_name_table(font):
    print("→ 📄 Generating name table...")
    name = font["name"] = newTable("name")
    name.names = [
        makeName(f"{FONT_NAME} Font", 1, 3, 1, 0x409),
        makeName("Regular", 2, 3, 1, 0x409),
        makeName(f"{FONT_NAME} Font Regular", 4, 3, 1, 0x409),
        makeName(f"Version {VERSION}", 5, 3, 1, 0x409),
        makeName(f"{FONT_NAME}FontRegular", 6, 3, 1, 0x409),
    ]
