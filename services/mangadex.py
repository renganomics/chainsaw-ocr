import os
import time

import requests
from ratelimit import limits, sleep_and_retry

BASE_URL = "https://api.mangadex.org"
timeout = 15


class MangaDexRequests:
    """Handles all interactions with the MangaDex API"""

    def __init__(self) -> None:
        self.session = requests.Session()

    def search_manga(self, title: str, language: str = "en") -> list[dict]:
        response = self.session.get(
            f"{BASE_URL}/manga",
            params={"title": title, "availableTranslatedLanguage[]": [language]},
            timeout=timeout,
        )

        response.raise_for_status()
        return response.json()["data"]

    def filter_by_language(self, results, language) -> list:
        return [
            manga for manga in results if manga["attributes"]["title"].get(language)
        ]

    def get_chapters(self, manga_id: str, language: str) -> list[dict[str, str | None]]:

        all_chapters = []
        offset = 0
        limit = 100  # Max MangaDex allows

        while True:
            try:
                response = self.session.get(
                    f"{BASE_URL}/manga/{manga_id}/feed",
                    params={
                        "translatedLanguage[]": [language],
                        "order[chapter]": "asc",
                        "limit": limit,
                        "offset": offset,
                    },
                    timeout=timeout,
                )

                response.raise_for_status()
                page = response.json()["data"]

                # Break when no more mages
                if not page:
                    break

                all_chapters.extend(page)
                offset += limit

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Offset {offset}: {e}")
                break

        # Only save if chapter is hosted natively on MangaDex site
        filtered_chapters = [
            chapter
            for chapter in all_chapters
            if chapter.get("attributes", {}).get("externalUrl") is None
        ]

        return [
            {
                "id": chapter["id"],
                "volume": chapter["attributes"].get("volume"),
                "chapter": chapter["attributes"].get("chapter"),
                "title": chapter["attributes"].get("title"),
            }
            for chapter in filtered_chapters
        ]

    # Add rate limit with extra 5-second buffer and retry after rest period
    @sleep_and_retry
    @limits(calls=20, period=65)
    def get_page_metadata(self, chapter_id: str) -> list[str]:

        for attempt in range(3):
            try:
                metadata = self.session.get(
                    f"{BASE_URL}/at-home/server/{chapter_id}", timeout=timeout
                )

                if metadata.status_code != 200:
                    raise RuntimeError(
                        f"Failed to fetch page metadata: {metadata.status_code}"
                    )
                # Retrieve required fields to build image url
                data = metadata.json()

                base_url = data["baseUrl"]
                chapter_hash = data["chapter"]["hash"]
                pages = data["chapter"]["data"]

                return [f"{base_url}/data/{chapter_hash}/{page}" for page in pages]

            except requests.exceptions.RequestException as e:
                print(f"[Retry {attempt + 1}] Failed for {chapter_id}: {e}")
                time.sleep(2**attempt)

        # After retries fail
        print(f"[Skipped] Chapter {chapter_id}")
        return []

    def download_url(self, image_url: str, filepath: str, filename: str) -> None:

        # Create filepath if non-existent
        os.makedirs(filepath, exist_ok=True)

        for attempt in range(3):
            try:
                response = self.session.get(image_url, timeout=timeout)
                response.raise_for_status()

                with open(f"{filepath}/{filename}.png", "wb") as file:
                    file.write(response.content)

                return

            # If request is successful write image data to png file
            except requests.exceptions.RequestException as e:
                print(f"[Retry {attempt + 1}] Image download failed: {e}")
                time.sleep(2**attempt)

        print(f"[Skipped image] {image_url}")
