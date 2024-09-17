import os
import sqlite3
import requests

BASE_API_URL = "https://api.mangadex.org"
DEFAULT_TITLE = "Chainsaw Man"


class Auth:

    TOKEN_URL = ("https://auth.mangadex.org/realms/mangadex/protocol/"
                 "openid-connect/token")

    def __init__(self, u=None, p=None, client=None, secret=None):
        self.u = u or os.environ["md_username"]
        self.p = p or os.environ["md_password"]
        self.client = client or os.environ["md_client"]
        self.secret = secret or os.environ["md_client_secret"]

    def token_request(self):
        credentials = {
            "grant_type": "password",
            "username": self.u,
            "password": self.p,
            "client_id": self.client,
            "client_secret": self.secret
        }

        try:
            r = requests.post(self.TOKEN_URL, data=credentials)
            r.raise_for_status()
            tokens = r.json()
            return (f"Access token: {tokens.get("access_token")}",
                    f"Refresh token: {tokens.get("refresh_token")}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching token: {e}")
            return None, None


class Search:

    def __init__(self, title=None, language="en"):
        self.title = title or DEFAULT_TITLE
        self.language = language
        self.search_results = []
        self.filtered_results = {}

    def title_search(self):
        base_url = f"{BASE_API_URL}/manga"
        r = requests.get(base_url, params={"title": self.title}).json()

        if r:
            for manga in r["data"]:
                self.search_results.append(manga["id"])
            print(f"Found {len(self.search_results)} results for '{self.title}'")
        else:
            print(f"Failed to retrieve search results for {self.title}")
        return self.search_results

    def language_filter(self):
        if not self.search_results:
            print(f"No search results found for {self.title}")
            return None

        manga_id = self.search_results[0]
        base_url = f"{BASE_API_URL}/manga/{manga_id}/feed"

        r = requests.get(base_url,
                         params={"translatedLanguage[]": self.language}).json()

        if r:
            filtered_chapter_ids = [chapter["id"] for chapter in r["data"]]
            attributes = [chapter["attributes"] for chapter in r["data"]]
            self.filtered_results = {
                "language": self.language,
                "chapter ids": filtered_chapter_ids,
                "attributes": attributes
            }
            return self.filtered_results
        else:
            print(f"Failed to fetch chapters for {self.title}")
            return None


class DatabaseStorage:

    def __init__(self, data=None):
        _search = Search() if not data else None
        if _search:
            _search.title_search()
            _search.language_filter()
            self.results = _search.filtered_results
        else:
            self.results = data

    def write_to_db(self, database_path="results"):
        if not self.results:
            print("No data to write to the database.")
            return

        try:
            with sqlite3.connect(f"{database_path}.db") as connection:
                cursor = connection.cursor()
                self.create_table(cursor)
                print(f"Table 'chapters' created")
                self.insert_chapters(cursor)
                print(f"Table 'chapters' populated")
                connection.commit()
                print(f"Database path is: '{database_path}.db'")
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

        for index, attribute in enumerate(self.results["attributes"]):
            volume_number = attribute.get("volume")
            chapter_number = attribute.get("chapter")
            chapter_title = attribute.get("title")
            chapter_id = self.results["chapter ids"]

            cursor.execute(
                "INSERT INTO chapters (volume_number, chapter_number, "
                "chapter_title, chapter_id, link) VALUES (?, ?, ?, ?, ?)",
                (volume_number, chapter_number, chapter_title,
                 chapter_id[index], f"{base_chapter_url}/{chapter_id[index]}")
            )


if __name__ == "__main__":

    # auth = Auth()
    # print(auth.token_request())

    search = Search(title=input("Enter a manga title: "))
    search.title_search()
    search.language_filter()

    store = DatabaseStorage(data=search.filtered_results)
    store.write_to_db()
