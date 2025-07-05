from fontTools.ttLib import newTable

def create_font_pscript_table(font, use_cff: bool = True):
    print("→ 📄 Generating postscript table...")
    post = font["post"] = newTable("post")
    post.formatType = 3.0
    post.isFixedPitch = 0
    post.italicAngle = 0.0
    post.minMemType1 = 0
    post.minMemType42 = 0
    post.maxMemType1 = 0
    post.maxMemType42 = 0
    post.underlinePosition = -75
    post.underlineThickness = 50
    post.extraNames = []
    post.mapping = {}
