import requests


class MangaDexRequests:

    def __init__(self):
        self.chapter_data = {}

    def get_manga_data(self, title, language):

        base_url = "https://api.mangadex.org"

        mangas = requests.get(
            f"{base_url}/manga",
            params={"title": title}
        )
        manga_id = [manga["id"] for manga in mangas.json()["data"]][0]

        chapters = requests.get(
            f"{base_url}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": language,
                    "order[chapter]": "asc"}
        )
        # print(chapters.json())
        chapter_ids = [chapter["id"] for chapter in chapters.json()["data"] if
                       chapter["attributes"]["externalUrl"] is None]
        attributes = [chapter["attributes"] for chapter in
                      chapters.json()["data"] if chapter["attributes"]
                      ["externalUrl"] is None]
        self.chapter_data = {"id": chapter_ids, "attributes": attributes}
        return self.chapter_data

    def get_page_metadata(self, chapter_id):
        pass

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
    print(mdx.get_manga_data("chainsaw man", "en"))
