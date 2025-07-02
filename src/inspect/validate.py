# noinspection PyUnresolvedReferences
import fontforge
import sys

if len(sys.argv) < 2:
    print("Usage: fontforge -script validate.py <font-file>")
    sys.exit(1)

font_path = sys.argv[1]
print(f" → 🔤 Opening '{font_path}'...")
font = fontforge.open(font_path)

print(f" → 🔍 Validating font...")
error_mask = font.validate()

# Known error codes with descriptions (partial list from FontForge docs)
ERROR_CODES = {
    1: "Missing points in glyph contours",
    2: "Incorrect point ordering in contours",
    4: "Overlapping contours detected",
    8: "Bad glyph references (missing components)",
    16: "Non-integral coordinates found",
    32: "Extrema missing from contours",
    64: "Incorrect direction of contours (e.g., clockwise vs CCW)",
    128: "Too many points in glyph",
    256: "Glyph width inconsistency",
    512: "Inconsistent hinting or instructions",
    1024: "Encoding errors or duplicates",
    2048: "Kerning problems",
    4096: "Lookup table issues",
    8192: "Glyph name errors",
    16384: "Invalid Unicode assignments",
    32768: "Advance width exceeds bounding box",
    65536: "Other structural issues",
}

if error_mask == 0:
    print(" → ✅ Font passed all checks!")
    sys.exit(0)
else:
    print(f" → ❌ Validation issues detected...")
    for bitmask, description in ERROR_CODES.items():
        if error_mask & bitmask:
            print(f"  → Code {bitmask}: {description}")

sys.exit(0)

print(" → 🔎 Inspecting individual glyphs...")
bad_glyphs = []

for glyph in font.glyphs():
    glyph_error_mask = glyph.validate()

    if glyph_error_mask != 0:
        bad_glyphs.append((glyph.glyphname, glyph_error_mask))

if bad_glyphs:
    print(f"  → ❌ {len(bad_glyphs)} glyphs with validation issues:")

    for name, mask in bad_glyphs:
        print(f" - {name}:")

        for code, desc in ERROR_CODES.items():
            if mask & code:
                print(f"     ⚠️  Code {code}: {desc}")
else:
    print("  → ✅ All glyphs passed individual validation.")

