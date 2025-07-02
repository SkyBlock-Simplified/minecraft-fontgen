from fontTools.ttLib import newTable

def create_tt_font_tables(font):
    print("→ 📄 Creating truetype table...")
    font["glyf"] = newTable("glyf")

    print(" → ➕ Adding fontforge compatibility...")
    font["prep"] = newTable("prep") # TT instructions pre-program
    font["prep"].program = [] # Dummy

    font["fpgm"] = newTable("fpgm") # Font program
    font["fpgm"].program = [] # Dummy

    font["cvt "] = newTable("cvt ") # Control values
    font["cvt "].values = [] # Dummy
