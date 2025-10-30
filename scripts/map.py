"""Sitemap downloader for Grokipedia"""
import requests
import xml.etree.ElementTree as ET
import os
from pathlib import Path

# === Configuration ===
# Get the scripts directory and navigate to grokipedia-sdk/grokipedia_sdk/links
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent / 'grokipedia-sdk' / 'grokipedia_sdk' / 'links'
SITEMAP_INDEX_URL = "https://grokipedia.com/sitemap.xml"
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"  # XML namespace

# Ensure base output folder exists
BASE_DIR.mkdir(parents=True, exist_ok=True)


def get_sitemap_links(sitemap_url):
    """Fetch and parse a sitemap or sitemap index, returning all <loc> URLs."""
    print(f"Fetching: {sitemap_url}")
    r = requests.get(sitemap_url, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    return [loc.text.strip() for loc in root.findall(f".//{NS}loc")]


if __name__ == '__main__':
    # === Step 1: Get all sitemap part URLs from the index ===
    part_urls = get_sitemap_links(SITEMAP_INDEX_URL)

    for sitemap_url in part_urls:
        # Example: https://assets.grokipedia.com/sitemap/sitemap-00001.xml
        part_name = os.path.basename(sitemap_url).replace(".xml", "")
        folder_path = BASE_DIR / part_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # === Step 2: Get page URLs from this sitemap ===
        urls = get_sitemap_links(sitemap_url)
        page_urls = [u for u in urls if "/page/" in u]
        slugs = [u.split("/page/")[1] for u in page_urls]

        # === Step 3: Save files ===
        urls_path = folder_path / "urls.txt"
        names_path = folder_path / "names.txt"

        with open(urls_path, "w", encoding="utf-8") as f:
            f.write("\n".join(page_urls))

        with open(names_path, "w", encoding="utf-8") as f:
            f.write("\n".join(slugs))

        print(f"✅ Saved {len(page_urls)} pages to {folder_path}")

    print("\nAll sitemap data downloaded successfully!")

