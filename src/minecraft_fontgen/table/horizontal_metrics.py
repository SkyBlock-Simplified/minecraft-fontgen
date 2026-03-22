from fontTools.ttLib import newTable

def create_font_hmetrics_table(font):
    """Creates an empty 'hmtx' table for horizontal glyph metrics (populated by GlyphStorage)."""
    font["hmtx"] = newTable("hmtx")
