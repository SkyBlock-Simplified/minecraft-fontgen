from file_io import read_providers_from_json_file, clean_output_dir, slice_providers_into_tiles
from font_creator import create_font_file
from src.util.config import OUTPUT_FILE, MINECRAFT_JAR_DEFAULT_JSON, OPENTYPE
from src.inspect.inspect import inspect_font_file

def main():
    clean_output_dir()
    providers = read_providers_from_json_file(MINECRAFT_JAR_DEFAULT_JSON)
    slice_providers_into_tiles(providers)
    glyph_storage = create_font_file(providers, OPENTYPE)
    glyph_storage.save(OUTPUT_FILE)
    inspect_font_file(OUTPUT_FILE)
    print("✨ Done.")

if __name__ == "__main__":
    main()
