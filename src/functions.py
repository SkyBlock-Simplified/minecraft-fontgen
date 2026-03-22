import requests

import src.config as config


def set_silent(value):
    """Sets the global silent mode flag."""
    config.SILENT = value


def is_silent():
    """Returns True if silent mode is enabled."""
    return config.SILENT


def log(*args, **kwargs):
    """Prints to stdout only when silent mode is disabled."""
    if not config.SILENT:
        print(*args, **kwargs)


def get_unicode_codepoint(unicode_char: str):
    """Converts a Unicode character string to its integer codepoint, handling surrogates."""
    try:
        utf16 = unicode_char.encode("utf-16", "surrogatepass")
        real_char = utf16.decode("utf-16")
        return ord(real_char)
    except Exception:
        return None

def get_font_type(bold = False, italic = False):
    """Returns the font style name (Regular, Bold, Italic, or BoldItalic)."""
    gtype = "Bold" if bold else "Regular"
    gtype = "Italic" if italic else gtype
    gtype = "BoldItalic" if bold and italic else gtype
    return gtype

def fetch_bytes(url, label=None):
    """Downloads raw bytes from a URL and returns the response content."""
    log(f"→ 🌐 Downloading {label or url}...")
    request = requests.get(url, timeout=30)
    request.raise_for_status()
    return request.content

def fetch_json(url, label=None):
    """Downloads and parses JSON from a URL."""
    log(f"→ 🌐 Downloading {label or url}...")
    request = requests.get(url, timeout=30)
    request.raise_for_status()
    return request.json()

def fetch_minecraft_resource(sha1, label=None):
    """Fetches a JSON resource from the Mojang CDN by its SHA-1 hash.
    (resources.download.minecraft.net/<first2>/<sha1>)"""
    return fetch_json(f"{config.MINECRAFT_RESOURCE_URL}/{sha1[:2]}/{sha1}", label=label)

def fetch_minecraft_resource_bytes(sha1, label=None):
    """Fetches raw bytes from the Mojang CDN by its SHA-1 hash."""
    return fetch_bytes(f"{config.MINECRAFT_RESOURCE_URL}/{sha1[:2]}/{sha1}", label=label)
