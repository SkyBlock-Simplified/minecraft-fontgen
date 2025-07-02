from xml.etree import ElementTree
from src.util.constants import UNITS_PER_EM, BITMAP_GLYPH_SIZE
from svgpathtools import Path, Line

class Svg:
    def __init__(self, svg_file):
        self.file = svg_file
        self.path = None

    def read_path(self):
        tree = ElementTree.parse(self.file)
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

        self.path = path

    def scale(self, glyph_height):
        if len(self.path) == 0:
            return self.path

        # Copy original
        path = Path(*self.path)

        # Align left edge
        min_x = min(seg.start.real for seg in path)
        path = path.translated(complex(-min_x, 0))

        # Align bottom (to 0), flip Y
        path = path.translated(complex(0, -glyph_height + 1))

        # Scale path from bitmap size (8px) to font units
        scale = UNITS_PER_EM / BITMAP_GLYPH_SIZE
        path = path.scaled(scale, -scale)

        return path
