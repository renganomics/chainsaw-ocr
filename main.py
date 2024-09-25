import requests
import sqlite3

from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

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

        # Only save data to lists if the chapter is hosted on the MangaDex site
        chapter_ids = [_chapter["id"] for _chapter in
                       chapter_response.json()["data"] if
                       _chapter["attributes"]["externalUrl"] is None]
        attributes = [_chapter["attributes"] for _chapter in
                      chapter_response.json()["data"] if
                      _chapter["attributes"]["externalUrl"] is None]

        # Save results to dictionary
        self.chapter_data = {"id": chapter_ids, "attributes": attributes}
        return self.chapter_data

    # Add rate limit with extra 5-second buffer and retry after rest period
    @sleep_and_retry
    @limits(calls=40, period=65)
    def get_page_metadata(self, _chapter_id):

        metadata = requests.get(
            f"{BASE_URL}/at-home/server/{_chapter_id}"
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

    def __init__(self, database_path):
        # Establish connection and cursor using given path
        with sqlite3.connect(f"{database_path}.db") as self.connection:
            self.cursor = self.connection.cursor()

    # Create table using given info and commit changes
    def create_table(self, name, columns):
        self.cursor.execute(f"CREATE TABLE {name} ({columns})")
        self.connection.commit()

    # Insert given info to table of choice and commit changes
    def insert_data(self, table, columns, values, data):
        self.cursor.execute(f"INSERT INTO {table} ({columns}) VALUES "
                            f"({values})", data)
        self.connection.commit()

    def retrieve_data(self, table, columns):
        table_data = self.cursor.execute(f"SELECT {columns} FROM {table}")
        return table_data.fetchall()


class ImageReader:

    def __init__(self, filepath):
        self.filepath = filepath

    def extract_text(self, page):
        pass

    def store_text(self, results):
        pass


if __name__ == "__main__":

    # Create MangaDexRequests instance and retrieve relevant manga data
    mdx = MangaDexRequests()
    mdx.get_manga_data(title="chainsaw man", language="en")

    db = Database("test")  # Create Database instance

    try:  # Create "chapters" table if non-existent
        db.create_table(
            name="chapters",
            columns="volume_number INTEGER,"
                    "chapter_number INTEGER,"
                    "title TEXT,"
                    "chapter_id TEXT,"
                    "chapter_link TEXT"
        )
        print("table chapters successfully created")

        # Iterate through chapter attributes and insert relevant data
        for index, chapter in enumerate(mdx.chapter_data["attributes"]):
            db.insert_data(
                table="chapters",
                columns="volume_number,"
                        "chapter_number,"
                        "title,"
                        "chapter_id,"
                        "chapter_link",
                values="?,?,?,?,?",
                data=(chapter["volume"],
                      chapter["chapter"],
                      chapter["title"],
                      mdx.chapter_data["id"][index],
                      f"https://mangadex.org/chapter/"
                      f"{mdx.chapter_data["id"][index]}")
            )
    except sqlite3.OperationalError as e:
        print(e)  # Print error if exception

    # Retrieve data from chapters table for use in page_links table
    chapters_db = db.retrieve_data(table="chapters", columns="*")

    try:  # Create page_links table if non-existent
        db.create_table(
            name="page_links",
            columns="volume_number INTEGER,"
                    "chapter_number INTEGER,"
                    "title TEXT,"
                    "page_number INTEGER,"
                    "link TEXT"
        )
        print("table page_links successfully created")

        # Iterate through rows in chapters table for relevant data
        for chapter in tqdm(chapters_db):
            volume_number = chapter[0]
            chapter_number = chapter[1]
            chapter_title = chapter[2]
            chapter_id = chapter[3]

            # Iterate through every page for each chapter and insert data
            for index, url in enumerate(mdx.get_page_metadata(chapter_id)):
                db.insert_data(
                    table="page_links",
                    columns="volume_number,"
                            "chapter_number,"
                            "title,"
                            "page_number,"
                            "link",
                    values="?,?,?,?,?",
                    data=(volume_number, chapter_number, chapter_title,
                          index + 1, url)
                )
    except sqlite3.OperationalError as e:
        print(e) # Print error if exception
