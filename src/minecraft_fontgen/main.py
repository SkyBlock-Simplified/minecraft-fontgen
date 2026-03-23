import sys
import io

from minecraft_fontgen.cli import parse_args
from minecraft_fontgen.piston import download_minecraft_assets
from minecraft_fontgen.file_io import clean_directories, parse_provider_file, build_glyph_map
from minecraft_fontgen.font_creator import create_font_files
from minecraft_fontgen.config import OUTPUT_FONT_NAME
from minecraft_fontgen.functions import set_silent, log, validate_fonts

# Force UTF-8 output to handle emoji in print statements
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def main():
    """Runs the font generation pipeline: download, parse, build glyph map, create fonts."""
    # Parse user provided arguments
    silent, output_dir, output_fonts, mc_version, use_cff, output_ext, validate = parse_args()
    set_silent(silent)

    # Clean work and output directories
    clean_directories(output_dir)

    # Download MC version, extract unifont + JAR assets
    matched_file, matched_format, unifont_glyphs = download_minecraft_assets(mc_version)

    # Parse provider glyphs from JAR bitmap PNGs (includes slicing)
    providers = parse_provider_file(matched_file, matched_format)

    # Build unified glyph map with pre-computed scaling
    glyph_map = build_glyph_map(providers, unifont_glyphs)

    # Generate all font files
    font_files = create_font_files(glyph_map, use_cff, output_fonts, output_dir, OUTPUT_FONT_NAME, output_ext)

    # Validate with FontForge (development only: --validate or FONTGEN_VALIDATE=1)
    if validate and font_files:
        validate_fonts(font_files)

    log("Done.")

if __name__ == "__main__":
    main()
