import os
import subprocess

def inspect_font_file(output_path):
    print(f"🕵️ Inspecting font...")
    result = subprocess.run(
        [
            "fontforge", "-lang=py", "-script",
            os.path.abspath("inspect/validate.py"),
            output_path
        ],
        encoding="utf-8", # Avoids UnicodeDecodeError
        errors="replace", # Replaces bad chars with �
        capture_output=True,
        text=True
    )

    print(result.stdout)
