import os

from collections import defaultdict
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

from src.config import UNITS_PER_EM, DEFAULT_GLYPH_SIZE, NOTDEF, NOTDEF_GLYPH
from src.functions import get_unicode_codepoint

class Glyph:
    def __init__(self, tile, use_cff: bool = True):
        self.unicode = tile["unicode"]
        self.codepoint = self._get_codepoint() if "codepoint" not in tile else tile["codepoint"]
        self.use_cff = use_cff
        self.name = self._get_name()
        self.svg = tile["svg"] if "svg" in tile else None
        self.size = tile["size"] or (DEFAULT_GLYPH_SIZE, DEFAULT_GLYPH_SIZE)
        self.ascent = tile["ascent"] if "ascent" in tile else 0

        # Pixels
        self.pixels = tile["pixels"] if "pixels" in tile else []
        self.width = self.pixels["width"] if "width" in self.pixels else DEFAULT_GLYPH_SIZE
        self.advance = self.pixels["advance"] if "advance" in self.pixels else DEFAULT_GLYPH_SIZE
        self.lsb = self.pixels["lsb"] if "lsb" in self.pixels else 0
        self.outer = self.pixels["paths"] if "paths" in self.pixels else {}
        self.holes = self.pixels["holes"] if "holes" in self.pixels else {}
        self.outer_scaled = {}
        self.holes_scaled = {}

        # Create pen
        self.pen = self._new_pen()

        # TODO: Reverse-engineer unscaled coordinates,
        #       pass the pixels and paths data for .notdef,
        #       let #scale and #draw handle this

        # Draw .notdef
        if self.codepoint == 0x0000:
            # Draw outer rectangle
            self.pen.moveTo((NOTDEF_GLYPH[0][0], NOTDEF_GLYPH[0][1]))
            self.pen.lineTo((NOTDEF_GLYPH[0][0], NOTDEF_GLYPH[0][3]))
            self.pen.lineTo((NOTDEF_GLYPH[0][2], NOTDEF_GLYPH[0][3]))
            self.pen.lineTo((NOTDEF_GLYPH[0][2], NOTDEF_GLYPH[0][1]))
            self.pen.closePath()

            # Draw inner rectangle
            self.pen.moveTo((NOTDEF_GLYPH[1][0], NOTDEF_GLYPH[1][1]))
            self.pen.lineTo((NOTDEF_GLYPH[1][0], NOTDEF_GLYPH[1][3]))
            self.pen.lineTo((NOTDEF_GLYPH[1][2], NOTDEF_GLYPH[1][3]))
            self.pen.lineTo((NOTDEF_GLYPH[1][2], NOTDEF_GLYPH[1][1]))
            self.pen.closePath()

    def draw(self):
        """
        Draws the outer contour and holes (as counter-clockwise subpaths) to a fontTools pen.
        Assumes:
            - self.corners contains the clockwise outer contour (list of (x, y) tuples)
            - self.holes is a dict with keys -> {'corners': [...]} representing holes
        """
        pen = self.pen

        def draw_contour(path):
            if len(path) >= 3:
                pen.moveTo(path[0])
                for pt in path[1:]:
                    pen.lineTo(pt)
                pen.closePath()

        # Draw outer shape (must be clockwise)
        for outer_path in self.outer_scaled:
            draw_contour(outer_path)

        # Draw holes (must be counter-clockwise)
        for hole_path in self.holes_scaled:
            draw_contour(list(reversed(hole_path)))

    def get(self):
        if self.use_cff:
            glyph = self.pen.getCharString()
        else:
            glyph = self.pen.glyph()

        return glyph

    def cpt(self):
        return self.codepoint in [0x0034, 0x0038, 0x0051, 0x0041, 0x00C0, 0x00CA]

    def scale(self):
        if not self.pixels:
            return

        if not self.pixels or all(len(p.get("corners", [])) < 3 for p in self.outer.values()):
            return

        outer_paths = [p["corners"] for p in self.outer.values() if len(p.get("corners", [])) >= 3]
        hole_paths = [h["corners"] for h in self.holes.values() if len(h.get("corners", [])) >= 3]

        all_points = [pt for path in outer_paths + hole_paths for pt in path]
        min_x = min(x for x, y in all_points)
        max_y = max(y for x, y in all_points)

        scale_x = UNITS_PER_EM / DEFAULT_GLYPH_SIZE
        scale_y = UNITS_PER_EM / DEFAULT_GLYPH_SIZE

        # TODO: Bounding box scaling correction might fix offset
        # Width = 16 × 8 = 128 pixels
        # The bounding box goes from x = 0 to x = 1152, so:
        # scale_x = 1152 / 128 = 9.0 units per pixel
        # scale_y = (896 - (-128)) / 8 = 1024 / 8 = 128.0 units per pixel

        #width, height = self.size
        #baseline_offset = self.ascent - height + 1
        baseline_offset = 0

        def transform(pt):
            x, y = pt
            return (x - min_x) * scale_x, (max_y - y + baseline_offset) * scale_y

        self.outer_scaled = [[transform(pt) for pt in path] for path in outer_paths]
        self.holes_scaled = [[transform(pt) for pt in path] for path in hole_paths]

    def valid(self):
        if self.codepoint is None:
            print(f" → ⚠️ Skipping invalid unicode '0x{self.codepoint:04X}'.")
            return False
        elif self.codepoint == 0x0000:
            return False

        return True

    def write_svg_paths(self, canvas_size=8):
        """
        Outputs a visual SVG of outer and hole paths.
        Outer paths = black fill, red stroke.
        Hole paths = white fill, blue stroke.
        """
        def path_to_d(path):
            return "M " + " L ".join(f"{x} {y}" for x, y in path) + " Z"

        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{canvas_size*32}" height="{canvas_size*32}" viewBox="0 0 {canvas_size} {canvas_size}"
         shape-rendering="crispEdges">
    <g stroke-width="0.05">'''

        def extract_corners(source):
            if isinstance(source, dict):
                return [p["corners"] for p in source.values() if "corners" in p]
            elif isinstance(source, list):
                return [p for p in source if isinstance(p, list) and len(p) >= 3]
            else:
                return []

        # Collect paths
        outer_paths = extract_corners(self.outer)
        hole_paths = extract_corners(self.holes)
        all_paths = outer_paths + hole_paths
        svg_paths = []

        # Draw filled paths
        for path in outer_paths:
            svg_paths.append(f'<path d="{path_to_d(path)}" fill="black" stroke="purple"/>')
        for path in hole_paths:
            svg_paths.append(f'<path d="{path_to_d(path)}" fill="white" stroke="blue"/>')

        # Track point usage across paths
        point_usage = defaultdict(int)
        for path in all_paths:
            unique_points = set(path)
            for pt in unique_points:
                point_usage[pt] += 1

        # Draw intersections
        for path in all_paths:
            for x, y in path:
                if point_usage[(x, y)] > 1:
                    svg_paths.append(f'<circle cx="{x}" cy="{y}" r="0.1" fill="red"/>')

        svg_footer = "</g></svg>"

        file_path = os.path.splitext(self.svg["file"])[0] + f"_paths.svg"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_header + "\n" + "\n".join(svg_paths) + "\n" + svg_footer)

    def _get_codepoint(self):
        return get_unicode_codepoint(self.unicode)

    def _get_name(self):
        if self.codepoint == 0x0000:
            return NOTDEF
        elif self.codepoint <= 0xFFFF:
            return f"uni{self.codepoint:04X}"
        else:
            return f"u{self.codepoint:06X}"

    def _new_pen(self):
        if self.use_cff:
            units_per_pixel = UNITS_PER_EM / DEFAULT_GLYPH_SIZE
            advance_width = round(self.width * units_per_pixel)
            return T2CharStringPen(advance_width, None)
        else:
            return TTGlyphPen(None)
