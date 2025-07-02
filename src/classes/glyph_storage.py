from collections import OrderedDict
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

from src.classes.unicode_char import UnicodeChar
from src.util.constants import ADVANCE_WIDTH, BOUNDING_BOX, UNITS_PER_EM, NOTDEF, NOTDEF_GLYPH

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

    def add(self, unicode: UnicodeChar, pen):
        name = unicode.get_name()
        self.glyphs[name] = self.get(pen)
        self.hmtx[name] = (ADVANCE_WIDTH, BOUNDING_BOX[0])

        if unicode.codepoint != 0x0000:
            self.cpr[0] = min(self.cpr[0], unicode.codepoint)
            self.cpr[1] = max(self.cpr[1], unicode.codepoint)

        # Add to glyph mapping
        for table in self.tables:
            if table.format == 4 and unicode.codepoint <= 0xFFFF: # Format 4 (BMP Codepoints)
                table.cmap[unicode.codepoint] = name
            elif table.format == 12 and unicode.codepoint > 0xFFFFFF: # Format 12 (SMP Codepoints)
                table.cmap[unicode.codepoint] = name

    def draw(self, svg_path):
        pen = self.new_pen()

        # Draw an empty contour for blank glyphs
        if not svg_path:
            pen.moveTo((0, 0))
            pen.endPath()
            return pen

        segments = list(svg_path.continuous_subpaths())

        for subpath in segments:
            if not subpath:
                continue

            current_pos = None
            for segment in subpath:
                start = (segment.start.real, segment.start.imag)
                end = (segment.end.real, segment.end.imag)

                if current_pos != start:
                    pen.moveTo(start)

                if segment.__class__.__name__ == 'Line':
                    pen.lineTo(end)
                elif segment.__class__.__name__ == 'CubicBezier':
                    pen.curveTo(
                        (segment.control1.real, segment.control1.imag),
                        (segment.control2.real, segment.control2.imag),
                        end
                    )
                elif segment.__class__.__name__ == 'QuadraticBezier':
                    pen.qCurveTo(
                        (segment.control.real, segment.control.imag),
                        end
                    )
                else:
                    pen.lineTo(end)

                current_pos = end

            # Ensure path is closed
            if abs(subpath[0].start - subpath[-1].end) < 1e-3:
                pen.closePath()
            else:
                pen.endPath()

        return pen

    def get(self, pen):
        if self.use_cff:
            glyph = pen.getCharString()
            glyph.width = ADVANCE_WIDTH
            glyph.private = self.top_dict.Private
        else:
            glyph = pen.glyph()

        return glyph

    def make_notdef(self):
        print(f"→ 🅽 Creating '{NOTDEF}' glyph...")
        pen = self.new_pen()

        # Draw rectangle using the bounding box
        pen.moveTo((NOTDEF_GLYPH[0], NOTDEF_GLYPH[1]))
        pen.lineTo((NOTDEF_GLYPH[0], NOTDEF_GLYPH[3]))
        pen.lineTo((NOTDEF_GLYPH[2], NOTDEF_GLYPH[3]))
        pen.lineTo((NOTDEF_GLYPH[2], NOTDEF_GLYPH[1]))
        pen.closePath()

        return self.get(pen)

    def new_pen(self):
        if self.use_cff:
            return T2CharStringPen(UNITS_PER_EM, None)
        else:
            return TTGlyphPen(None)

    def save(self):
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

        # Ensure .notdef is assigned to index 0
        for table in self.tables:
            table.cmap[0x0000] = NOTDEF

    def sort(self):
        # Create .notdef and add it to the front
        notdef_glyph = self.make_notdef()
        self.hmtx[NOTDEF] = (ADVANCE_WIDTH, BOUNDING_BOX[0])
        self.glyphs.pop(NOTDEF, None)
        self.glyphs = OrderedDict([(NOTDEF, notdef_glyph)] + list(self.glyphs.items()))
