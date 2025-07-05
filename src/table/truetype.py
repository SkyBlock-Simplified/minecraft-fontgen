import numpy as np

from fontTools.ttLib import newTable
from fontTools.ttLib.tables.ttProgram import Program

def create_tt_font_tables(font):
    print("→ 📄 Creating truetype table...")
    font["glyf"] = newTable("glyf")
    font["glyf"].glyphs = {}

    font["loca"] = newTable("loca") # Automatically populated

    print(" → ➕ Adding fontforge compatibility...")
    font["prep"] = newTable("prep") # TT instructions pre-program
    font["prep"].program = Program() # Dummy

    font["fpgm"] = newTable("fpgm") # Font program
    font["fpgm"].program = Program() # Dummy

    font["cvt "] = newTable("cvt ") # Control values
    font["cvt "].values = np.zeros(0, dtype=np.int16) # Dummy
