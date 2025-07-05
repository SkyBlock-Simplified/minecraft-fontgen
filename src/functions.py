import requests

from src.config import MOJANG_MANIFEST_URL

def get_unicode_codepoint(unicode_char: str):
    try:
        utf16 = unicode_char.encode("utf-16", "surrogatepass")
        real_char = utf16.decode("utf-16")
        return ord(real_char)
    except Exception:
        return None

def get_minecraft_versions():
    response = requests.get(MOJANG_MANIFEST_URL)
    response.raise_for_status()
    data = response.json()
    return data["versions"]  # List of dicts with id, url, etc.

def get_client_jar_url(version_id):
    versions = get_minecraft_versions()
    version = next(v for v in versions if v["id"] == version_id)
    version_meta = requests.get(version["url"]).json()
    return version_meta["downloads"]["client"]["url"]

def download_client_jar(version_id, output_file):
    jar_url = get_client_jar_url(version_id)
    response = requests.get(jar_url, stream=True)
    response.raise_for_status()
    with open(output_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)