import os
import time
import sqlite3
import requests

from tqdm import tqdm

BASE_API_URL = "https://api.mangadex.org"
MANGADEX_TOKEN_URL = f"{BASE_API_URL}/realms/mangadex/protocol/openid-connect/token"
DEFAULT_TITLE = "Chainsaw Man"


class Auth:
    TOKEN_URL = "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token"

    def __init__(self, u=None, p=None, client=None, secret=None):
        self.u = u or os.environ["md_username"]
        self.p = p or os.environ["md_password"]
        self.client = client or os.environ["md_client"]
        self.secret = secret or os.environ["md_client_secret"]

    def token_request(self):
        # Create POST request for authentication token using user data
        credentials = {
            "grant_type": "password",
            "username": f"{self.u}",
            "password": f"{self.p}",
            "client_id": f"{self.client}",
            "client_secret": f"{self.secret}"
        }

        try:
            r = requests.post(self.TOKEN_URL, data=credentials)
            r.raise_for_status()
            # Return access and refresh tokens
            tokens = r.json()
            return tokens.get("access_token"), tokens.get("refresh_token")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching token: {e}")
            return None, None


class Requests:

    @staticmethod
    def safe_request(url, params=None):
        while True:
            try:
                r = requests.get(url, params=params)
                r.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

                # Check if the response contains valid JSON
                if r.headers.get('Content-Type') == 'application/json':
                    try:
                        return r.json()  # Return the parsed JSON response
                    except requests.exceptions.JSONDecodeError as e:
                        print(f"Error parsing JSON from {url}: {e}")
                        print(f"Response content: {r.text}")  # Log the actual response content
                        return None
                else:
                    print(f"Non-JSON response from {url}, status code: {r.status_code}")
                    print(f"Response content: {r.text}")
                    return None

            except requests.exceptions.RequestException as e:
                print(f"Error occurred during request to {url}: {e}")
                return None


class Search:
    """Conduct searches through API from user input"""

    def __init__(self, title: str = None, language: str = "en"):
        # Create default parameter for title if left blank
        self.title = title or DEFAULT_TITLE

        self.language = language
        self.search_results = []
        self.filtered_results = {}

    def title_search(self):
        base_url = "https://api.mangadex.org"

        r = Requests.safe_request(
            f"{base_url}/manga",
            params={"title": self.title}
        )

        if r:  # Ensure response is valid
            # Compiles results into list
            [self.search_results.append(manga["id"]) for manga in r["data"]]
        else:
            print(f"Failed to retrieve search results for {self.title}")
        return self.search_results

    def language_filter(self):
        if not self.search_results:
            print(f"No search results found for {self.title}")
            return None

        manga_id = self.search_results[0]
        base_url = "https://api.mangadex.org"

        r = Requests.safe_request(
            f"{base_url}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": self.language},
        )

        if r:  # Ensure response is valid
            # Compile dictionaries of selected data
            filtered_chapter_ids = [chapter["id"] for chapter in r["data"]]
            chapter_attributes = [chapter["attributes"] for chapter in r["data"]]

            self.filtered_results = {"language": self.language,
                                     "chapter ids": filtered_chapter_ids,
                                     "attributes": chapter_attributes}
            return self.filtered_results
        else:
            print(f"Failed to fetch chapters for {self.title}")
            return None


class DatabaseStorage:
    """Writes retrieved data to SQLite database of user's choice"""

    def __init__(self, data: dict = None):
        # Create default results if parameter is left blank
        _search = Search() if not data else None
        if _search:
            _search.title_search()
            _search.language_filter()
            self.results = _search.filtered_results
        else:
            self.results = data

    def write_to_db(self, database_path="chainsaw"):
        if not self.results:
            print("No data to write to the database.")
            return

        try:
            with sqlite3.connect(f"{database_path}.db") as connection:
                cursor = connection.cursor()
                self.create_table(cursor)
                self.insert_chapters(cursor)
                connection.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    @staticmethod
    def create_table(cursor):
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS chapters("
            "volume_number INTEGER,"
            "chapter_number INTEGER,"
            "chapter_title TEXT,"
            "chapter_id TEXT,"
            "link TEXT)"
        )

    def insert_chapters(self, cursor):
        base_chapter_url = "https://mangadex.org/chapter"

        # Populate rows in each column with appropriate data
        for index, attribute in enumerate(self.results["attributes"]):
            volume_number = attribute["volume"]
            chapter_number = attribute["chapter"]
            chapter_title = attribute["title"]
            chapter_id = self.results["chapter ids"]

            cursor.execute(
                "INSERT INTO chapters "
                "(volume_number, chapter_number, chapter_title, chapter_id, link) "
                "VALUES (?,?,?,?,?)",
                (volume_number,
                 chapter_number,
                 chapter_title,
                 chapter_id[index],
                 f"{base_chapter_url}/{chapter_id[index]}")
            )


class Downloader:

    def __init__(self, database_path="chainsaw.db"):
        self.database_path = database_path

    def page_links(self):
        base_url = "https://api.mangadex.org/at-home/server"

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()

            # Create a table in database to store links
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS page_links("
                "volume_number INTEGER,"
                "chapter_number INTEGER,"
                "links TEXT)"
            )
            connection.commit()

            chapter_info = cursor.execute(
                "SELECT volume_number, chapter_number, chapter_id FROM chapters"
            ).fetchall()

            # Use tqdm to track chapter downloads progress
            for (volume, chapter, chapter_id) in tqdm(chapter_info, desc="Downloading chapters", unit="chapter"):
                r = Requests.safe_request(f"{base_url}/{chapter_id}")
                if r:
                    # Retrieve data and create links for each page
                    base_url = r["baseUrl"]
                    chapter_hash = r["chapter"]["hash"]
                    pages = r["chapter"]["data"]

                    links = [f"{base_url}/data/{chapter_hash}/{page}" for page in pages]

                    cursor.execute(
                        "INSERT INTO page_links (volume_number, chapter_number, links) "
                        "VALUES (?, ?, ?)",
                        (volume, chapter, ",".join(links))
                    )
                else:
                    print(f"Failed to retrieve page links for chapter {chapter_id}")

            connection.commit()


if __name__ == "__main__":
    search = Search(title=input("Enter a manga title: "))
    search.title_search()
    search.language_filter()

    store = DatabaseStorage(data=search.filtered_results)
    store.write_to_db()

    dldr = Downloader()
    dldr.page_links()
