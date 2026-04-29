import os

import requests
from ratelimit import limits, sleep_and_retry

BASE_URL = "https://api.mangadex.org"


class MangaDexRequests:
    """Handles all interactions with the MangaDex API"""

    def get_manga_data(self, title: str, languages: str) -> dict[str, list]:

        try:
            # Retrieve all manga ids that correspond to title and save first result
            manga_response = requests.get(
                f"{BASE_URL}/manga", params={"title": title}, timeout=10
            )

            if manga_response.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch manga: {manga_response.status_code}"
                )

            manga_data = manga_response.json()["data"]

            if not manga_data:
                raise RuntimeError(f"No manga found for given title: {title}")

            manga_id = manga_data[0]["id"]

            # Retrieve all chapters in given language in ascending order
            chapter_response = requests.get(
                f"{BASE_URL}/manga/{manga_id}/feed",
                params={"translatedLanguage[]": languages, "order[chapter]": "asc"},
                timeout=10,
            )

            if chapter_response.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch chapters: {chapter_response.status_code}"
                )

            chapter_json = chapter_response.json()

            # Only save if chapter is hosted natively on MangaDex site
            filtered_chapters = [
                _chapter
                for _chapter in chapter_json["data"]
                if _chapter["attributes"]["externalUrl"] is None
            ]

            chapter_ids = [_chapter["id"] for _chapter in filtered_chapters]
            attributes = [_chapter["attributes"] for _chapter in filtered_chapters]

            # Save result lists to dictionary
            chapter_data = {"id": chapter_ids, "attributes": attributes}

            return chapter_data

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed while fetching manga data: {e}")

    # Add rate limit with extra 5-second buffer and retry after rest period
    @sleep_and_retry
    @limits(calls=40, period=65)
    def get_page_metadata(self, chapter_id: str) -> list[str]:

        try:
            metadata = requests.get(
                f"{BASE_URL}/at-home/server/{chapter_id}", timeout=10
            )

            if metadata.status_code != 200:
                raise RuntimeError(
                    f"Failed to fetch page metadata: {metadata.status_code}"
                )
            # Retrieve required fields to build image url
            metadata_json = metadata.json()

            base_url = metadata_json["baseUrl"]
            chapter_hash = metadata_json["chapter"]["hash"]
            chapter_data = metadata_json["chapter"]["data"]

            page_links = [
                f"{base_url}/data/{chapter_hash}/{page}" for page in chapter_data
            ]

            return page_links

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed while fetching page metadata: {e}")

    @staticmethod
    def download_url(image_url: str, filepath: str, filename: str) -> None:

        # Create filepath if non-existent
        os.makedirs(filepath, exist_ok=True)

        try:
            image_response = requests.get(image_url, timeout=10)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Image download failed: {e}")

        # If request is successful write image data to png file
        if image_response.status_code != 200:
            raise RuntimeError(
                f"Failed to download image, status code: {image_response.status_code}"
            )
        with open(f"{filepath}/{filename}.png", "wb") as file:
            file.write(image_response.content)
