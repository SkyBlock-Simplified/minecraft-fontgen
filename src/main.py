from file_io import clean_directories, slice_providers_into_tiles, read_providers_from_file
from font_creator import create_font_file
from src.config import OUTPUT_FONT_FILE, OPENTYPE, OUTPUT_FONTS, OUTPUT_FONT_EXT
from src.file_io import get_minecraft_assets

def main():
    clean_directories()
    matched_file, matched_format = get_minecraft_assets()
    providers = read_providers_from_file(matched_file, matched_format)

    for font in OUTPUT_FONTS:
        slice_providers_into_tiles(providers, font[1], font[2])
        glyph_storage = create_font_file(providers, OPENTYPE, font[1], font[2])
        output_file = f"{OUTPUT_FONT_FILE}-{font[0]}.{OUTPUT_FONT_EXT}"
        glyph_storage.save(output_file)
        #inspect_font_file(output_file)
    print("✨ Done.")

if __name__ == "__main__":
    main()
