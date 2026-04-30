import os

from tqdm import tqdm

from utils.paths import safe_filename


def download_chapter(client, chapter_id: str, attrs: dict, base_dir="downloads"):
    volume = attrs.get("volume") or "unknown"
    chapter_num = attrs.get("chapter") or "unknown"
    title = attrs.get("title") or "no_title"

    safe_title = safe_filename(title)

    folder = f"{base_dir}/volume_{volume}/chapter_{chapter_num}-{safe_title}"

    os.makedirs(folder, exist_ok=True)

    # Get all page URLs
    page_urls = client.get_page_metadata(chapter_id)

    # Skip if empty (failed retries)
    if not page_urls:
        print(f"[Skipped] No pages for volume {volume} chapter {chapter_num}: {title}")
        return None

    for i, url in enumerate(tqdm(page_urls, desc=f"Ch {chapter_num}")):
        client.download_url(image_url=url, filepath=folder, filename=f"page_{i + 1}")

    return folder
