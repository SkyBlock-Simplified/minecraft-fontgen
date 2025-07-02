from file_io import read_json_file, clean_output_dir
from font_creator import create_font_file
from print_cff_debug_info import print_cff_debug_info
from src.util.config import OUTPUT_FILE_PATH, MINECRAFT_JAR_DEFAULT_JSON, OPENTYPE



def main():
    # Clean previous output
    clean_output_dir()

    # Load providers
    providers = read_json_file(MINECRAFT_JAR_DEFAULT_JSON)

    # Create font file
    glyph_storage = create_font_file(providers, OPENTYPE)

    # Save font file
    print_cff_debug_info(glyph_storage.font)
    glyph_storage.font.save(OUTPUT_FILE_PATH)

    # Validate font file

    print("✨ Done.")

if __name__ == "__main__":
    main()
