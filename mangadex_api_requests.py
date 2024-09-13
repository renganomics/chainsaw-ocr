import os
import sqlite3
import requests


class TokenRequest:
    """Executes requests to the MangaDex API"""
    def __init__(self,
                 u=os.environ["md_username"],
                 p=os.environ["md_password"],
                 client=os.environ["md_client"],
                 secret=os.environ["md_client_secret"]):
        self.u = u
        self.p = p
        self.client = client
        self.secret = secret

    def token_request(self):
        """Create POST request for authentication token using user data"""
        credentials = {
            "grant_type": "password",
            "username": f"{self.u}",
            "password": f"{self.p}",
            "client_id": f"{self.client}",
            "client_secret": f"{self.secret}"
        }

        post = requests.post(
            "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect"
            "/token",
            data=credentials
        )

        post_json = post.json()
        access_token = post_json["access_token"]
        refresh_token = post_json["refresh_token"]
        return f"Access token: {access_token}\nRefresh token: {refresh_token}"


class Search:
    """Conduct searches through API using user input"""
    def __init__(self, title="Chainsaw Man", languages="en"):
    # Create default parameter for title if left blank
        if title == "":
            self.title = "Chainsaw Man"
        elif title != "":
            self.title = title

        self.languages = languages
        self.search_results = []
        self.filtered_results = {}

    def title_search(self):
        base_url = "https://api.mangadex.org"

        r = requests.get(
            f"{base_url}/manga",
            params={"title": self.title}
        )
    # Compiles results into list
        for manga in r.json()["data"]:
            self.search_results.append(manga["id"])
        return self.search_results

    def language_filter(self):
        manga_id = self.search_results[0]
        base_url = "https://api.mangadex.org"

        r = requests.get(
            f"{base_url}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": self.languages},
        )
    # Compile dictionaries of selected data
        chapter_attributes = [chapter["attributes"] for chapter in r.json()["data"]]
        filtered_chapter_ids = [chapter["id"] for chapter in r.json()["data"]]

        self.filtered_results = {"languages": self.languages,
                                 "chapter ids": filtered_chapter_ids,
                                 "attributes": chapter_attributes}
        return self.filtered_results


class DatabaseStorage:
    """Writes retrieved data to database of user's choice"""
    def __init__(self, database_path=None, results=None):
        self.database_path = database_path

    # Create default results if parameter is left blank
        if results is None or results == "":
            _search = Search()
            _search.title_search()
            _search.language_filter()
            self.results = _search.filtered_results
        elif results is not None:
            self.results = results

    def write_to_db(self):
    # Create default database_path if parameter is left blank
        if self.database_path is None or self.database_path == "":
            self.database_path = "chainsaw"
        elif self.database_path is not None:
            self.database_path = self.database_path

    # If path does not already exist, write to it
        count = 0
        if not os.path.exists(f"{self.database_path}.db"):
            connection = sqlite3.connect(f"{self.database_path}.db")
            cursor = connection.cursor()

        # Create table and populate with columns
            cursor.execute(
                "CREATE TABLE chapters("
                "volume_number INTEGER,"
                "chapter_number INTEGER,"
                "chapter_title TEXT,"
                "chapter_id TEXT,"
                "link TEXT)"
            )
        # Populate rows in each column with appropriate data
            for attribute in self.results["attributes"]:
                volume_number = attribute["volume"]
                chapter_number = attribute["chapter"]
                chapter_title = attribute["title"]
                chapter_id = self.results["chapter ids"]
                cursor.execute(
                    "INSERT INTO chapters "
                    "(volume_number,"
                    "chapter_number, "
                    "chapter_title, "
                    "chapter_id, "
                    "link) "
                    "VALUES (?,?,?,?,?)",
                    (volume_number,
                     chapter_number,
                     chapter_title,
                     chapter_id[count],
                     f"https://mangadex.org/chapter/{chapter_id[count]}")
                )
                count = count + 1
            connection.commit()
    # If path exists already, raise exception
        elif os.path.exists(f"{self.database_path}.db"):
            raise FileExistsError("This path already exists.")


if __name__ == "__main__":
    search_prompt = input("Enter a manga title: ")
    search = Search(search_prompt, "en")
    search.title_search()
    search.language_filter()
    db_path_prompt = input("Enter a path for the database to be stored: ")
    store = DatabaseStorage(database_path=db_path_prompt,
                            results=search.filtered_results)
    store.write_to_db()
