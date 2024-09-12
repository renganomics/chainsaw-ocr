import os
import requests
import sqlite3

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

    def __init__(self, title="Chainsaw Man", languages="en"):
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

        chapter_attributes = [chapter["attributes"] for chapter in r.json()["data"]]
        filtered_chapter_ids = [chapter["id"] for chapter in r.json()["data"]]

        self.filtered_results = {"languages": self.languages,
                                 "chapter ids": filtered_chapter_ids,
                                 "attributes": chapter_attributes}
        return self.filtered_results


class DatabaseStorage:

    def __init__(self, database_path="chainsaw.db", results=None):
        self.database_path = database_path
        self.results = results

        if results is None:
            search = Search()
            search.title_search()
            search.language_filter()
            self.results = search.filtered_results

        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        count = 0
        for attribute in self.results["attributes"]:
            volume_number = attribute["volume"]
            chapter_number = attribute["chapter"]
            chapter_title = attribute["title"]
            chapter_id = self.results["chapter ids"]
            cursor.execute("INSERT INTO chapters (volume_number, "
                           "chapter_number, chapter_title, chapter_id) VALUES (?,?,?,?)",
                           (volume_number, chapter_number, chapter_title, chapter_id[count]))
            count = count + 1

        connection.commit()


if __name__ == "__main__":
    # search = Search("Chainsaw Man", "en")
    # search.title_search()
    # search.language_filter()
    # store = DatabaseStorage(database_path="chainsaw.db", results=search.filtered_results)#
    DatabaseStorage()
