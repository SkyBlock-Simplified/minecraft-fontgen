from file_io import clean_directories, slice_providers_into_tiles, read_providers_from_file
from font_creator import create_font_file
from src.config import OUTPUT_FONT_FILE, OPENTYPE
from src.file_io import get_minecraft_assets

def main():
    clean_directories()
    matched_file, matched_format = get_minecraft_assets()
    providers = read_providers_from_file(matched_file, matched_format)
    # TODO: Bold and Italic
    slice_providers_into_tiles(providers)
    glyph_storage = create_font_file(providers, OPENTYPE)
    glyph_storage.save(OUTPUT_FONT_FILE)
    #inspect_font_file(OUTPUT_FONT_FILE)
    print("✨ Done.")

if __name__ == "__main__":
    main()
