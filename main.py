import requests
import sqlite3
import os
import pytesseract

from ratelimit import limits, sleep_and_retry
from tqdm import tqdm
from PIL import Image, ImageOps

BASE_URL = "https://api.mangadex.org"


class MangaDexRequests:
    """Handles all interactions with the MangaDex API"""

    def __init__(self):
        self.chapter_data = {}
        self.page_links = []

    def get_manga_data(self, title, languages):
        try:
            # Retrieve all manga ids that correspond to title and save first result
            manga_response = requests.get(
                f"{BASE_URL}/manga",
                params={"title": title}
            )
            manga_id = [manga["id"] for manga in manga_response.json()["data"]][0]

            # Retrieve all chapters in given language in ascending order
            chapter_response = requests.get(
                f"{BASE_URL}/manga/{manga_id}/feed",
                params={"translatedLanguage[]": languages,
                        "order[chapter]": "asc"}
            )

            # Only save if chapter is hosted natively on MangaDex site
            chapter_ids = [_chapter["id"] for _chapter in
                           chapter_response.json()["data"] if
                           _chapter["attributes"]["externalUrl"] is None]
            attributes = [_chapter["attributes"] for _chapter in
                          chapter_response.json()["data"] if
                          _chapter["attributes"]["externalUrl"] is None]

            # Save result lists to dictionary
            self.chapter_data = {"id": chapter_ids, "attributes": attributes}
            return self.chapter_data
        except requests.exceptions.ConnectionError as e:
            print(e)

    # Add rate limit with extra 5-second buffer and retry after rest period
    @sleep_and_retry
    @limits(calls=40, period=65)
    def get_page_metadata(self, _chapter_id):
        try:
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
        except requests.exceptions.ConnectionError as e:
            print(e)

    @staticmethod
    def download_url(image_url, filepath, filename):
        # Create filepath if non-existent
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        image_response = requests.get(image_url)

        # If request is successful write image data to png file
        if image_response.status_code != 200:
            print(f"Failed to download image, status code: "
                  f"{image_response.status_code}")
        else:
            with open(f"{filepath}/{filename}.png", "wb") as file:
                file.write(image_response.content)


class Database:
    """Handles all database interactions"""

    def __init__(self, database_path):
        # Establish connection and cursor using given path
        with sqlite3.connect(f"{database_path}.db") as self.connection:
            self.cursor = self.connection.cursor()

    # Create table using given info and commit changes
    def create_table(self, name, columns):
        try:
            self.cursor.execute(f"CREATE TABLE {name} ({columns})")
            self.connection.commit()
            print(f"table {name} successfully created")
        except sqlite3.OperationalError as e:
            print(e)

    # Insert given info to table of choice and commit changes
    def insert_data(self, table, columns, data):
        try:
            # Add values according to number of given data
            data_count = len(data)
            values = ("?," * data_count).strip(",")

            self.cursor.execute(f"INSERT INTO {table} ({columns}) VALUES "
                                f"({values})", data)
            self.connection.commit()
        except sqlite3.OperationalError as e:
            print(e)

    # Retrieve relevant data from chosen table and columns
    def retrieve_data(self, table, columns):
        try:
            table_data = self.cursor.execute(f"SELECT {columns} FROM {table}")
            return table_data.fetchall()
        except sqlite3.OperationalError as e:
            print(e)


class ImageReader:
    """Handles Tesseract-OCR and file interactions"""

    def __init__(self):
        self.png_list = []

    def scan_folder(self, parent):
        # Iterate over files in parent directory for png files
        for file in os.listdir(parent):
            if file.endswith(".png"):
                self.png_list.append(f"{parent}/{file}")
            else:
                # Add file to path
                current_path = "".join((parent, "/", file))
                # Call method for every subdirectory if it is a folder
                if os.path.isdir(current_path):
                    ImageReader.scan_folder(self, parent=current_path)
        return self.png_list

    @staticmethod
    def extract_text(image_path, scale_factor=2):
        # Turn image greyscale to improve readability
        with Image.open(image_path, mode="r") as image:
            grey_image = ImageOps.grayscale(image)

            # Resize image to improve readability
            resized_image = grey_image.resize(
                (grey_image.width * scale_factor,
                 grey_image.height * scale_factor),
                resample=Image.Resampling.LANCZOS
            )

            # Extract text and store to string
            _extracted_text = pytesseract.image_to_string(resized_image)
        return _extracted_text

    @staticmethod
    def store_text(results, filepath, filename):
        # Create filepath if non-existent
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Write OCR results to text file of choice
        with open(f"{filepath}/{filename}.txt", "w") as file:
            file.write(results)


if __name__ == "__main__":

    mdx = MangaDexRequests()
    mdx.get_manga_data(title="chainsaw man", languages="en")

    test_directory = "test"
    db = Database(test_directory)
    if not os.path.exists(f"{test_directory}.db"):
        db.create_table(
            name="chapters",
            columns="volume_number INTEGER,"
                    "chapter_number INTEGER,"
                    "title TEXT,"
                    "chapter_id TEXT,"
                    "chapter_link TEXT"
        )

        # Iterate over chapter attributes and insert relevant data
        for index, chapter in enumerate(mdx.chapter_data["attributes"]):
            db.insert_data(
                table="chapters",
                columns="volume_number,"
                        "chapter_number,"
                        "title,"
                        "chapter_id,"
                        "chapter_link",
                data=(chapter["volume"],
                      chapter["chapter"],
                      chapter["title"],
                      mdx.chapter_data["id"][index],
                      f"https://mangadex.org/chapter/"
                      f"{mdx.chapter_data["id"][index]}")
            )

        chapters_db = db.retrieve_data(table="chapters", columns="*")

        db.create_table(
            name="page_links",
            columns="volume_number INTEGER,"
                    "chapter_number INTEGER,"
                    "title TEXT,"
                    "page_number INTEGER,"
                    "link TEXT"
        )

        for chapter in tqdm(chapters_db):
            volume_number = chapter[0]
            chapter_number = chapter[1]
            chapter_title = chapter[2]
            chapter_id = chapter[3]

            # Iterate over every page for each chapter and insert data
            for index, url in enumerate(mdx.get_page_metadata(chapter_id)):
                db.insert_data(
                    table="page_links",
                    columns="volume_number,"
                            "chapter_number,"
                            "title,"
                            "page_number,"
                            "link",
                    data=(volume_number, chapter_number, chapter_title,
                          index + 1, url)
                )

    # Retrieve page_links data and establish parent folder for downloads
    page_links_data = db.retrieve_data(table="page_links", columns="*")
    image_download_dir = "test_download"

    if not os.path.exists(image_download_dir):
        for page_link in tqdm(page_links_data):
            volume_number = page_link[0]
            chapter_number = page_link[1]
            chapter_title = page_link[2].replace(" ", "_").replace("/", "_")
            page_number = page_link[3]
            url = page_link[4]

            # Use retrieved values to create directories within download folder
            download_directory = (
                f"{image_download_dir}/volume_{volume_number}/"
                f"chapter_{chapter_number}-{chapter_title}"
            )
            # Download each page and save to respective directory
            mdx.download_url(
                image_url=url,
                filepath=f"{download_directory}",
                filename=f"page_{page_number}"
            )
    else:
        print(f"parent directory {image_download_dir} already exists")

    image_directory = "test_download"
    img = ImageReader()
    img.scan_folder(image_directory)
    print(img.png_list)
