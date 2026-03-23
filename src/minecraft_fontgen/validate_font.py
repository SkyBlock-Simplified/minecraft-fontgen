# noinspection PyUnresolvedReferences
import fontforge
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: fontforge -script validate_font.py <font-file> [font-file ...]")
    sys.exit(1)

# FontForge glyph-level validation bitmasks
GLYPH_ERRORS = {
    0x1:     "Open contour",
    0x2:     "Self-intersecting contour",
    0x4:     "Wrong direction contour",
    0x8:     "Flipped reference",
    0x10:    "Missing extrema",
    0x20:    "Unknown referenced glyph",
    0x40:    "Mixed references and contours",
    0x80:    "Non-integral coordinates",
    0x100:   "Overlapping PS hints",
    0x200:   "Too many PS hints",
    0x400:   "Bad references",
    0x800:   "Non-integral advance width",
    0x1000:  "Bad transformation matrix",
    0x2000:  "Bad PS hint masks",
    0x4000:  "Points too far apart",
    0x8000:  "Non-integral coordinates in reference",
    0x10000: "Missing anchor points",
    0x20000: "Duplicate glyph name",
    0x40000: "Duplicate unicode codepoint",
    0x80000: "Overlapping contours",
}

MAX_SAMPLES = 8

for font_path in sys.argv[1:]:
    print(f"{'=' * 60}")
    print(f" {font_path}")
    print(f"{'=' * 60}")
    font = fontforge.open(font_path)

    total_glyphs = 0
    clean_glyphs = 0
    error_buckets = defaultdict(list)

    for glyph in font.glyphs():
        total_glyphs += 1
        mask = glyph.validate()
        if mask == 0:
            clean_glyphs += 1
            continue
        for code, desc in GLYPH_ERRORS.items():
            if mask & code:
                error_buckets[code].append(glyph.glyphname)

    bad_count = total_glyphs - clean_glyphs

    if bad_count == 0:
        print(f" All {total_glyphs} glyphs passed validation.")
    else:
        print(f" {clean_glyphs}/{total_glyphs} glyphs clean, {bad_count} with issues:")
        print()
        for code in sorted(error_buckets.keys()):
            names = error_buckets[code]
            desc = GLYPH_ERRORS.get(code, f"Unknown (0x{code:X})")
            sample = ", ".join(names[:MAX_SAMPLES])
            suffix = f" ... +{len(names) - MAX_SAMPLES} more" if len(names) > MAX_SAMPLES else ""
            print(f"  0x{code:05X} {desc}")
            print(f"          {len(names)} glyphs: {sample}{suffix}")
            print()

    print()
    font.close()
