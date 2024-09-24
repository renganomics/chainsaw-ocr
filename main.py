import requests

BASE_URL = "https://api.mangadex.org"


class MangaDexRequests:

    def __init__(self):
        self.chapter_data = {}
        self.page_links = []

    def get_manga_data(self, title, language):

        # Retrieve all manga ids that correspond to title and save first result
        manga_response = requests.get(
            f"{BASE_URL}/manga",
            params={"title": title}
        )
        manga_id = [manga["id"] for manga in manga_response.json()["data"]][0]

        # Retrieve all chapters in given language
        chapter_response = requests.get(
            f"{BASE_URL}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": language,
                    "order[chapter]": "asc"}
        )

        # Only save data if the chapter is hosted on the MangaDex site
        chapter_ids = [chapter["id"] for chapter in
                       chapter_response.json()["data"] if chapter["attributes"]
                       ["externalUrl"] is None]
        attributes = [chapter["attributes"] for chapter in
                      chapter_response.json()["data"] if chapter["attributes"]
                      ["externalUrl"] is None]

        # Save results to dictionary
        self.chapter_data = {"id": chapter_ids, "attributes": attributes}
        return self.chapter_data

    def get_page_metadata(self, chapter_id):

        metadata = requests.get(
            f"{BASE_URL}/at-home/server/{chapter_id}"
        )

        # Retrieve required fields to build image url
        base_url = metadata.json()["baseUrl"]
        chapter_hash = metadata.json()["chapter"]["hash"]
        chapter_data = metadata.json()["chapter"]["data"]

        # Save results to list
        self.page_links = [f"{base_url}/data/{chapter_hash}/{page}" for page in
                           chapter_data]
        return self.page_links

    @staticmethod
    def download_url(image_url, filename):
        image_response = requests.get(image_url)

        # If request is successful write image data to png file
        if image_response.status_code != 200:
            print(f"Failed to download image, status code: "
                  f"{image_response.status_code}")
        else:
            with open(f"{filename}.png", "wb") as file:
                file.write(image_response.content)
            print("Image successfully downloaded.")


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
    mdx.get_manga_data(title="chainsaw man", language="en")
    mdx.get_page_metadata(chapter_id="73af4d8d-1532-4a72-b1b9-8f4e5cd295c9")
    print(mdx.page_links)
    mdx.download_url(image_url=mdx.page_links[-1], filename="test")
