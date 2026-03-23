import argparse
import os

from minecraft_fontgen.config import OUTPUT_DIR, OUTPUT_FONTS

VALID_STYLES = {"regular", "bold", "italic", "bolditalic"}


def _load_env_file(path=".env"):
    """Loads key=value pairs from a .env file into os.environ (won't overwrite existing vars)."""
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value


def parse_args():
    """Parses CLI arguments with env var fallbacks. Returns (silent, output_dir, output_fonts, mc_version, validate)."""
    _load_env_file()

    parser = argparse.ArgumentParser(description="Minecraft bitmap font to OpenType/TrueType converter.")
    parser.add_argument("--silent", action="store_true", default=None,
                        help="Suppress all output except errors")
    parser.add_argument("--output", type=str, default=None,
                        help="Override output directory")
    parser.add_argument("--version", type=str, default=None,
                        help="Minecraft version to use (skips interactive prompt)")
    parser.add_argument("--styles", type=str, default=None,
                        help="Comma-separated font styles: regular,bold,italic,bolditalic")
    parser.add_argument("--validate", action="store_true", default=None,
                        help="Run FontForge validation on generated fonts (requires fontforge)")

    args = parser.parse_args()

    # --- silent ---
    if args.silent is not None and args.silent:
        silent = True
    elif os.environ.get("FONTGEN_SILENT", "").lower() in ("1", "true", "yes"):
        silent = True
    else:
        silent = False

    # --- output_dir ---
    if args.output is not None:
        output_dir = args.output
    elif os.environ.get("FONTGEN_OUTPUT"):
        output_dir = os.environ["FONTGEN_OUTPUT"]
    else:
        output_dir = OUTPUT_DIR

    # --- styles ---
    raw_styles = None
    if args.styles is not None:
        raw_styles = args.styles
    elif os.environ.get("FONTGEN_STYLES"):
        raw_styles = os.environ["FONTGEN_STYLES"]

    if raw_styles is not None:
        requested = {s.strip().lower() for s in raw_styles.split(",")}
        invalid = requested - VALID_STYLES
        if invalid:
            parser.error(f"Invalid style(s): {', '.join(sorted(invalid))}. "
                         f"Valid options: {', '.join(sorted(VALID_STYLES))}")
        output_fonts = [
            (name, name.lower() in requested, bold, italic)
            for name, _, bold, italic in OUTPUT_FONTS
        ]
    else:
        output_fonts = OUTPUT_FONTS

    # --- version ---
    if args.version is not None:
        mc_version = args.version
    elif os.environ.get("FONTGEN_VERSION"):
        mc_version = os.environ["FONTGEN_VERSION"]
    else:
        mc_version = None

    # --- validate ---
    if args.validate is not None and args.validate:
        validate = True
    elif os.environ.get("FONTGEN_VALIDATE", "").lower() in ("1", "true", "yes"):
        validate = True
    else:
        validate = False

    return silent, output_dir, output_fonts, mc_version, validate
