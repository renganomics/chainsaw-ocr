import os

import requests
from ratelimit import limits, sleep_and_retry

BASE_URL = "https://api.mangadex.org"


class MangaDexRequests:
    """Handles all interactions with the MangaDex API"""

    def __init__(self):
        self.chapter_data = {}
        self.page_links = []

    def get_manga_data(self, title, languages):
        try:
            # Retrieve all manga ids that correspond to title and save first result
            manga_response = requests.get(f"{BASE_URL}/manga", params={"title": title})
            manga_id = [manga["id"] for manga in manga_response.json()["data"]][0]

            # Retrieve all chapters in given language in ascending order
            chapter_response = requests.get(
                f"{BASE_URL}/manga/{manga_id}/feed",
                params={"translatedLanguage[]": languages, "order[chapter]": "asc"},
            )

            # Only save if chapter is hosted natively on MangaDex site
            chapter_ids = [
                _chapter["id"]
                for _chapter in chapter_response.json()["data"]
                if _chapter["attributes"]["externalUrl"] is None
            ]
            attributes = [
                _chapter["attributes"]
                for _chapter in chapter_response.json()["data"]
                if _chapter["attributes"]["externalUrl"] is None
            ]

            # Save result lists to dictionary
            self.chapter_data = {"id": chapter_ids, "attributes": attributes}
            return self.chapter_data
        except requests.exceptions.ConnectionError as e:
            print(e)

    # Add rate limit with extra 5-second buffer and retry after rest period
    @sleep_and_retry
    @limits(calls=40, period=65)
    def get_page_metadata(self, _chapter_id) -> list[str]:
        try:
            metadata = requests.get(f"{BASE_URL}/at-home/server/{_chapter_id}")

            # Retrieve required fields to build image url
            base_url = metadata.json()["baseUrl"]
            chapter_hash = metadata.json()["chapter"]["hash"]
            chapter_data = metadata.json()["chapter"]["data"]

            # Save results to list
            self.page_links = [
                f"{base_url}/data/{chapter_hash}/{page}" for page in chapter_data
            ]
            return self.page_links
        except requests.exceptions.ConnectionError as e:
            print(e)
            return []  # Retrun empty list to avoid NoneType error

    @staticmethod
    def download_url(image_url, filepath, filename):
        # Create filepath if non-existent
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        image_response = requests.get(image_url)

        # If request is successful write image data to png file
        if image_response.status_code != 200:
            print(
                f"Failed to download image, status code: {image_response.status_code}"
            )
        else:
            with open(f"{filepath}/{filename}.png", "wb") as file:
                file.write(image_response.content)
