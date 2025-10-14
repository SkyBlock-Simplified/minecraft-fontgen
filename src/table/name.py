from fontTools.ttLib import newTable
from fontTools.ttLib.tables._n_a_m_e import makeName
from src.functions import get_font_type

from src.config import (
    FONT_NAME, VERSION,
    MANUFACTURER, DESIGNER,
    VENDOR_URL, DESIGNER_URL,
    DESCRIPTION, COPYRIGHT,
    SAMPLE_TEXT
)

# Helpers
def _ps_sanitize(s: str) -> str:
    """
    PostScript name must be ASCII, <= 63 chars, no spaces.
    Replace spaces with hyphens and strip disallowed chars.
    """
    import re, unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.replace(" ", "-")
    s = re.sub(r"[^A-Za-z0-9\-\._]", "", s)
    return s[:63] or "UntitledPS"

# We’ll write each record for three platforms for robustness:
_PLATFORMS = [
    (3, 1, 0x0409),  # Windows, Unicode BMP, en-US
    (1, 0, 0),       # Mac, Roman, English
    (0, 3, 0),       # Unicode, Unicode 2.0 BMP, (lang 0)
]

def _add(name_table, name_id, text):
    if text is None:
        return
    for (plat, enc, lang) in _PLATFORMS:
        name_table.names.append(makeName(text, name_id, plat, enc, lang))

def create_font_name_table(font, bold = False, italic = False):
    print("→ 📄 Generating name table...")
    name = font["name"] = newTable("name")
    name.names = []
    gtype = get_font_type(bold, italic)

    family      = f"{FONT_NAME} Font"                 # NameID 1
    subfamily   = gtype                               # NameID 2
    full_name   = f"{FONT_NAME} Font {gtype}"         # NameID 4
    version_str = f"Version {VERSION}"                # NameID 5
    ps_name     = _ps_sanitize(f"{FONT_NAME}{gtype}") # NameID 6

    # Recommended “typographic” names (IDs 16/17) mirror 1/2 for simple families
    typo_family    = f"{FONT_NAME}"                   # Often just brand family without "Font"
    typo_subfamily = gtype

    # Unique font identifier (NameID 3) — common format: “Version X;Manufacturer;Family Subfamily”
    unique_id = f"{version_str};{MANUFACTURER or 'Unknown'};{full_name}"

    # Core required/expected
    _add(name, 0,  COPYRIGHT or f"Copyright © {MANUFACTURER or FONT_NAME} {VERSION}")
    _add(name, 1,  family)
    _add(name, 2,  subfamily)
    _add(name, 3,  unique_id)
    _add(name, 4,  full_name)
    _add(name, 5,  version_str)
    _add(name, 6,  ps_name)

    # Nice-to-have / commonly present fields
    #_add(name, 7,  TRADEMARK)
    _add(name, 8,  MANUFACTURER)
    _add(name, 9,  DESIGNER)
    _add(name, 10, DESCRIPTION)
    _add(name, 11, VENDOR_URL)
    _add(name, 12, DESIGNER_URL)
    #_add(name, 13, LICENSE_TEXT)
    #_add(name, 14, LICENSE_URL)

    # Typographic (Preferred) family/subfamily
    _add(name, 16, typo_family)
    _add(name, 17, typo_subfamily)

    # Compatible Full (often equals Full Name; include if you want)
    _add(name, 18, full_name)

    # Sample text (helpful in testers)
    _add(name, 19, SAMPLE_TEXT or "The quick brown fox jumps over the lazy dog. 0123456789")

    # WWS family/subfamily (optional; used for “Weight/Width/Slope only” families)
    # If you don't manage a large family with WWS names, you can omit these.
    # _add(name, 21, typo_family)
    # _add(name, 22, typo_subfamily)
