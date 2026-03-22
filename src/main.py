import sys
import io

from src.cli import parse_args
from src.piston import read_minecraft_piston_api
from src.file_io import clean_directories, read_providers_from_file, build_glyph_map
from src.font_creator import create_font_files
from src.config import OPENTYPE, OUTPUT_FONT_EXT, OUTPUT_FONT_NAME
from src.functions import set_silent, log

# Force UTF-8 output to handle emoji in print statements
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def main():
    """Runs the font generation pipeline: download, parse, build glyph map, create fonts."""
    # Parse user provided arguments
    silent, output_dir, output_fonts = parse_args()
    set_silent(silent)

    # Clean work and output directories
    clean_directories(output_dir)

    # Download MC version, extract unifont + JAR assets
    matched_file, matched_format, unifont_glyphs = read_minecraft_piston_api()

    # Parse provider glyphs from JAR bitmap PNGs (includes slicing)
    providers = read_providers_from_file(matched_file, matched_format)

    # Build unified glyph map with pre-computed scaling
    glyph_map = build_glyph_map(providers, unifont_glyphs)

    # Generate all font files
    create_font_files(glyph_map, OPENTYPE, output_fonts, output_dir, OUTPUT_FONT_NAME, OUTPUT_FONT_EXT)

    log("Done.")

if __name__ == "__main__":
    main()
