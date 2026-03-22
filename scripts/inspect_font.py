import os
import subprocess

def inspect_font_file(output_path):
    """Runs FontForge validation on a font file via subprocess."""
    print(f"🕵️ Inspecting font...")
    result = subprocess.run(
        [
            "fontforge", "-lang=py", "-script",
            os.path.abspath("scripts/validate_font.py"),
            output_path
        ],
        encoding="utf-8", # Avoids UnicodeDecodeError
        errors="replace", # Replaces bad chars with �
        capture_output=True,
        text=True
    )

    print(result.stdout)
