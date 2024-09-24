import requests

BASE_URL = "https://api.mangadex.org"


class MangaDexRequests:

    def __init__(self):
        self.chapter_data = {}

    def get_manga_data(self, title, language):

        mangas = requests.get(
            f"{BASE_URL}/manga",
            params={"title": title}
        )
        manga_id = [manga["id"] for manga in mangas.json()["data"]][0]

        chapters = requests.get(
            f"{BASE_URL}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": language,
                    "order[chapter]": "asc"}
        )
        # print(chapters.json())

        chapter_ids = [chapter["id"] for chapter in chapters.json()["data"]
                       if chapter["attributes"]["externalUrl"] is None]
        attributes = [chapter["attributes"] for chapter in
                      chapters.json()["data"] if chapter["attributes"]
                      ["externalUrl"] is None]
        self.chapter_data = {"id": chapter_ids, "attributes": attributes}
        return self.chapter_data

    @staticmethod
    def get_page_metadata(chapter_id):

        metadata = requests.get(
            f"{BASE_URL}/at-home/server/{chapter_id}"
        )
        # print(metadata.json())
        base_url = metadata.json()["baseUrl"]
        chapter_hash = metadata.json()["chapter"]["hash"]
        chapter_data = metadata.json()["chapter"]["data"]

        page_links = [f"{base_url}/data/{chapter_hash}/{page}" for page in
                      chapter_data]
        return page_links

    def download_url(self, image_url, filepath):
        pass


class Database:

    def __init__(self, cursor):
        self.cursor = cursor

    def create_table(self, name, columns):
        pass

    def insert_data(self, table, columns, values, data):
        pass


class PageUrls(Database):

    def retrieve_chapter_ids(self, table, columns):
        pass

    def create_table(self, name, columns):
        pass

    def insert_data(self, table, columns, values, data):
        pass


class ImageReader:

    def __init__(self, filepath):
        self.filepath = filepath

    def extract_text(self, page):
        pass

    def store_text(self, results):
        pass


if __name__ == "__main__":
    mdx = MangaDexRequests()
    mdx.get_manga_data("chainsaw man", "en")
    print(mdx.get_page_metadata("73af4d8d-1532-4a72-b1b9-8f4e5cd295c9"))
