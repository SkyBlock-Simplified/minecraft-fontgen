import os
import zipfile
import requests

from six import BytesIO

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
    manifest = response.json()

    def filter_type(type):
        return {
            v["id"]: {
                "type": v["type"],
                "url": v["url"]
            }
            for v in manifest["versions"] if v["type"] == type}

    return {
        "release": filter_type("release"),
        "snapshot": filter_type("snapshot")
    }

def get_minecraft_client_jar_url(version_url):
    version_meta = requests.get(version_url)
    version_meta.raise_for_status()
    return version_meta.json()["downloads"]["client"]["url"]

def get_minecraft_jar_data(jar_url):
    response = requests.get(jar_url, stream=True)
    response.raise_for_status()
    return BytesIO(response.content)

def extract_font_assets(jar_data, output_path):
    os.makedirs(output_path, exist_ok=True)
    extracted = []

    with zipfile.ZipFile(jar_data) as jar:
        for file in jar.namelist():
            if file.endswith("default.json") or "font/" in file:
                jar.extract(file, path=output_path)
                extracted.append(file)

    return extracted