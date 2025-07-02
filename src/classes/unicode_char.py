class UnicodeChar:
    def __init__(self, char):
        self.char = char
        self.codepoint = self.get_codepoint()

    def get_codepoint(self):
        try:
            utf16 = self.char.encode("utf-16", "surrogatepass")
            real_char = utf16.decode("utf-16")
            return ord(real_char)
        except Exception:
            return None

    def get_name(self):
        # Reuse existing glyph name if available in any cmap table
        # existing_name = None
        # for table in font["cmap"].tables:
        # if table.isUnicode():
        # existing_name = table.cmap.get(codepoint)
        # if existing_name:
        # return existing_name

        if self.codepoint <= 0xFFFF:
            return f"uni{self.codepoint:04X}"
        else:
            return f"u{self.codepoint:06X}"
