from collections import OrderedDict

from fontTools.ttLib.standardGlyphOrder import standardGlyphOrder

from src.glyph.glyph import Glyph
from src.util.constants import ADVANCE_WIDTH, BOUNDING_BOX, NOTDEF, DEFAULT_GLYPH_SIZE

class GlyphStorage:
    def __init__(self, font, use_cff: True):
        print("→ 📄 Creating glyph storage...")
        self.font = font
        self.tables = font["cmap"].tables
        self.use_cff = use_cff
        self.glyphs = OrderedDict()
        self.cpr = [0xFFFFFF, 0]
        self.hmtx = {}

        if self.use_cff:
            cff = font["CFF "]
            self.top_dict = cff.cff.topDictIndex[0]
            self.charstrings = self.top_dict.CharStrings
        else:
            self.glyf = font["glyf"]

    def add(self, glyph: Glyph):
        name = glyph.name
        self.hmtx[name] = (ADVANCE_WIDTH, BOUNDING_BOX[0])

        # Draw font glyph
        font_glyph = glyph.get()
        if self.use_cff:
            font_glyph.width = ADVANCE_WIDTH
            font_glyph.private = self.top_dict.Private
        self.glyphs[name] = font_glyph

        # Update min/max codepoint
        if glyph.codepoint != 0x0000:
            self.cpr[0] = min(self.cpr[0], glyph.codepoint)
            self.cpr[1] = max(self.cpr[1], glyph.codepoint)

        # Add to glyph mapping
        for table in self.tables:
            if table.format == 4 and glyph.codepoint <= 0xFFFF: # Format 4 (BMP Codepoints)
                table.cmap[glyph.codepoint] = name
            elif table.format == 12: # Format 12 (SMP Codepoints)
                table.cmap[glyph.codepoint] = name

    def add_notdef(self):
        self.add(Glyph({
            "unicode": None,
            "codepoint": 0x0000,
            "size": (DEFAULT_GLYPH_SIZE, DEFAULT_GLYPH_SIZE),
            "location": (0, 0),
            "output": None
        }, self.use_cff))

    def get(self, pen):
        if self.use_cff:
            glyph = pen.getCharString()
            glyph.width = ADVANCE_WIDTH
            glyph.private = self.top_dict.Private
        else:
            glyph = pen.glyph()

        return glyph

    def new_glyph(self, tile):
        return Glyph(tile, self.use_cff)

    def save(self, output_file):
        print(f"→ 💾 Saving font to '{output_file}'...")
        self.font.save(output_file)

    def write(self):
        # Sort glyphs
        self.glyphs = OrderedDict([(NOTDEF, self.glyphs[NOTDEF])] + list(self.glyphs.items()))

        # Set glyph order
        self.font.setGlyphOrder(list(self.glyphs.keys()))

        # Set glyph mappings
        if self.use_cff:
            self.top_dict.charset = list(self.glyphs.keys())

            for name, glyph in self.glyphs.items():
                self.charstrings[name] = glyph
        else:
            self.glyf.glyphOrder = self.font.getGlyphOrder()

            for name, glyph in self.glyphs.items():
                self.glyf.glyphs[name] = glyph

        # Set glyph metrics
        total_glyphs = len(self.glyphs)
        self.font["hmtx"].metrics = self.hmtx
        self.font["hhea"].numberOfHMetrics = total_glyphs # Number of advanceWidth + leftSideBearing pairs in the hmtx table
        self.font["maxp"].numGlyphs = total_glyphs # Total number of glyphs in the font
        self.font["OS/2"].usFirstCharIndex = self.cpr[0] # First Unicode codepoint in the font
        self.font["OS/2"].usLastCharIndex = self.cpr[1] # Last Unicode codepoint in the font