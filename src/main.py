from file_io import read_json_file, clean_output_dir
from font_creator import create_font_file
from src.util.config import OUTPUT_FILE_PATH, MINECRAFT_JAR_DEFAULT_JSON, OPENTYPE
from src.inspect.inspect import inspect_font_file

def main():
    # Clean previous output
    clean_output_dir()

    # Load providers
    providers = read_json_file(MINECRAFT_JAR_DEFAULT_JSON)

    # Create font file
    glyph_storage = create_font_file(providers, OPENTYPE)

    # Save font file
    glyph_storage.save(OUTPUT_FILE_PATH)

    # Inspect font file
    inspect_font_file(OUTPUT_FILE_PATH)

    print("✨ Done.")

if __name__ == "__main__":
    main()
