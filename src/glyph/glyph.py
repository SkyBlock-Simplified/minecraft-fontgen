from xml.etree import ElementTree

from PIL.ImagePath import Path
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from svgpathtools import Line

from src.util.constants import UNITS_PER_EM, BITMAP_GLYPH_SIZE, NOTDEF, NOTDEF_GLYPH
from src.util.functions import get_unicode_codepoint

class Glyph:
    def __init__(self, unicode, codepoint: int = None, use_cff: bool = True, svg_file: str = None, provider = None):
        self.unicode = unicode
        self.codepoint = codepoint if codepoint else self._get_codepoint()
        self.use_cff = use_cff
        self.name = self._get_name()
        self.svg_file = svg_file
        self.svg_path = None
        self.width = provider["glyph_width"] if provider else BITMAP_GLYPH_SIZE
        self.height = provider["glyph_height"] if provider else BITMAP_GLYPH_SIZE
        self.pen = self._new_pen()

        if codepoint == 0x0000:
            # Draw rectangle using the bounding box
            self.pen.moveTo((NOTDEF_GLYPH[0], NOTDEF_GLYPH[1]))
            self.pen.lineTo((NOTDEF_GLYPH[0], NOTDEF_GLYPH[3]))
            self.pen.lineTo((NOTDEF_GLYPH[2], NOTDEF_GLYPH[3]))
            self.pen.lineTo((NOTDEF_GLYPH[2], NOTDEF_GLYPH[1]))
            self.pen.closePath()

    def draw(self):
        pen = self._new_pen()

        # Draw an empty contour for blank glyphs
        if not self.svg_path:
            pen.moveTo((0, 0))
            pen.endPath()
            self.pen = pen
            return

        segments = list(self.svg_path.continuous_subpaths())

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

        self.pen = pen

    def get(self):
        if self.use_cff:
            glyph = self.pen.getCharString()
        else:
            glyph = self.pen.glyph()

        return glyph

    def read_path(self):
        tree = ElementTree.parse(self.svg_file)
        root = tree.getroot()
        path = Path()

        for rect in root.iter('{http://www.w3.org/2000/svg}rect'):
            x = float(rect.attrib.get('x', 0))
            y = float(rect.attrib.get('y', 0))
            w = float(rect.attrib.get('width', 1))
            h = float(rect.attrib.get('height', 1))

            # Create square as 4 lines (clockwise)
            p1 = complex(x, y)
            p2 = complex(x + w, y)
            p3 = complex(x + w, y + h)
            p4 = complex(x, y + h)

            # Add closed square as 4 lines + close
            square = Path(
                Line(p1, p2),
                Line(p2, p3),
                Line(p3, p4),
                Line(p4, p1) # Close loop
            )

            path.extend(square)

        self.svg_path = path

    def scale(self):
        if len(self.svg_path) == 0:
            return

        # Copy original
        path = Path(*self.svg_path)

        # Align left edge
        min_x = min(seg.start.real for seg in path)
        path = path.translated(complex(-min_x, 0))

        # Align bottom (to 0), flip Y
        path = path.translated(complex(0, -self.height + 1))

        # Scale path from bitmap size (8px) to font units
        scale = UNITS_PER_EM / BITMAP_GLYPH_SIZE
        path = path.scaled(scale, -scale)

        self.svg_path = path

    def valid(self):
        if self.codepoint is None:
            print(f" → ⚠️ Skipping invalid unicode '0x{self.codepoint:04X}'.")
            return False
        elif self.codepoint == 0x0000:
            return False

        return True

    def _get_codepoint(self):
        return get_unicode_codepoint(self.unicode)

    def _get_name(self):
        # Reuse existing glyph name if available in any cmap table
        # existing_name = None
        # for table in font["cmap"].tables:
        # if table.isUnicode():
        # existing_name = table.cmap.get(codepoint)
        # if existing_name:
        # return existing_name

        if self.codepoint == 0x0000:
            return NOTDEF
        elif self.codepoint <= 0xFFFF:
            return f"uni{self.codepoint:04X}"
        else:
            return f"u{self.codepoint:06X}"

    def _new_pen(self):
        if self.use_cff:
            return T2CharStringPen(UNITS_PER_EM, None)
        else:
            return TTGlyphPen(None)
