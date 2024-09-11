import os
import requests


class MangaDex:
    """Executes various requests to the MangaDex API"""

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
        """ Create POST request for authentication token using user data"""
        creds = {
            "grant_type": "password",
            "username": f"{self.u}",
            "password": f"{self.p}",
            "client_id": f"{self.client}",
            "client_secret": f"{self.secret}"
        }

        post = requests.post(
            "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect"
            "/token",
            data=creds
        )

        post_json = post.json()
        access_token = post_json["access_token"]
        refresh_token = post_json["refresh_token"]
        return f"Access token: {access_token}\nRefresh token: {refresh_token}"

    @staticmethod
    def title_search(title="Chainsaw Man"):
        base_url = "https://api.mangadex.org"

        r = requests.get(
            f"{base_url}/manga",
            params={"title": title}
        )
        search_results = [manga["id"] for manga in r.json()["data"]]
        return search_results

    @staticmethod
    def language_filter(manga_id, languages="en"):
        base_url = "https://api.mangadex.org"

        r = requests.get(
            f"{base_url}/manga/{manga_id}/feed",
            params={"translatedLanguage[]": languages},
        )

        filtered_by_lang = [chapter["id"] for chapter in r.json()["data"]]
        return {"language": languages,
                "filtered chapters": filtered_by_lang}


if __name__ == "__main__":
    mangadex = MangaDex()
    chainsaw_man = mangadex.title_search()[0]
    print(chainsaw_man)
    print(mangadex.language_filter(manga_id=chainsaw_man))
    # print(mangadex.token_request())
