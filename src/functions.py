import os
import zipfile
import requests

from six import BytesIO

from src.config import MINECRAFT_MANIFEST_URL, MINECRAFT_RESOURCE_URL


def get_unicode_codepoint(unicode_char: str):
    try:
        utf16 = unicode_char.encode("utf-16", "surrogatepass")
        real_char = utf16.decode("utf-16")
        return ord(real_char)
    except Exception:
        return None

def get_font_type(bold = False, italic = False):
    gtype = "Bold" if bold else "Regular"
    gtype = "Italic" if italic else gtype
    gtype = "BoldItalic" if bold and italic else gtype
    return gtype

def fetch_minecraft_versions():
    """
    Fetches the latest Minecraft version details, including releases and snapshots, from the
    Minecraft manifest URL. The returned data contains categorized details based on version
    type, i.e., release or snapshot.

    :return: A dictionary containing the latest version information and categorized version
        lists. The dictionary structure includes:

        - "latest": A dictionary with "release" and "snapshot" latest version IDs.
        - "releases": A dictionary of all released versions, with their IDs as keys.
        - "snapshots": A dictionary of all snapshot versions, with their IDs as keys.
    :rtype: dict
    """
    response = requests.get(MINECRAFT_MANIFEST_URL)
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
        "latest": {
            "release": manifest["latest"]["release"],
            "snapshot": manifest["latest"].get("snapshot")
        },
        "releases": filter_type("release"),
        "snapshots": filter_type("snapshot")
    }

def fetch_minecraft_version_entry(selected_version, version_url):
    print(f"→ ☕ Downloading {selected_version}.json...")
    version_data = requests.get(version_url, timeout=30)
    version_data.raise_for_status()
    return version_data.json()

def fetch_minecraft_asset_index(asset_index):
    print(f"→ ☕ Downloading {asset_index['sha1']}/{asset_index['id']}.json...")
    asset_index_data = requests.get(asset_index["url"], timeout=30)
    asset_index_data.raise_for_status()
    return asset_index_data.json()

def fetch_minecraft_asset(sha1):
    # Mojang CDN layout: resources.download.minecraft.net/<first2>/<sha1>
    return f"{MINECRAFT_RESOURCE_URL}/{sha1[:2]}/{sha1}"

def fetch_minecraft_client_jar_url(version_url):
    version_meta = requests.get(version_url, timeout=30)
    version_meta.raise_for_status()
    return version_meta.json()["downloads"]["client"]["url"]

def fetch_minecraft_jar_data(jar_url):
    response = requests.get(jar_url, timeout=30, stream=True)
    response.raise_for_status()
    return BytesIO(response.content)

def save_jar_to_disk(jar_data, output_path):
    with open(f"{output_path}/minecraft.jar", "wb") as f:
        f.write(jar_data.getbuffer())

def extract_font_assets(jar_data, output_path):
    os.makedirs(output_path, exist_ok=True)
    extracted = []

    with zipfile.ZipFile(jar_data) as jar:
        for file in jar.namelist():
            if file.endswith("default.json") or "font/" in file:
                jar.extract(file, path=output_path)
                extracted.append(file)

    return extracted