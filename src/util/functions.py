from fontTools.ttLib import TTFont

def progress_bar(current: int, total: int, padding: int = 2, width: int = 40):
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '-' * (width - filled)
    left_pad = ' ' * padding
    print(f"\r{left_pad}[{bar}] {current}/{total}", end='', flush=True)

def get_unicode_codepoint(unicode_char: str):
    try:
        utf16 = unicode_char.encode("utf-16", "surrogatepass")
        real_char = utf16.decode("utf-16")
        return ord(real_char)
    except Exception:
        return None

def get_unicode_name(codepoint: int, font: TTFont):
    # Re-use existing glyph name if available in any cmap table
    existing_name = None
    for table in font["cmap"].tables:
        if table.isUnicode():
            existing_name = table.cmap.get(codepoint)
            if existing_name:
                return existing_name

    if codepoint <= 0xFFFF:
        return f"uni{codepoint:04X}"
    else:
        return f"u{codepoint:06X}"
