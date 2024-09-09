import os
import json
import requests

u = os.environ["md_username"]
p = os.environ["md_password"]
client = os.environ["md_client"]
secret = os.environ["md_client_secret"]

# Create GET and POST requests
# creds = {
#     "grant_type": "password",
#     "username": f"{u}",
#     "password": f"{p}",
#     "client_id": f"{client}",
#     "client_secret": f"{secret}"
# }
#
# response = requests.get(
#     "https://api.mangadex.org/statistics/manga/a77742b1-befd-49a4-bff5-1ad4e6b0ef7b")
# post = requests.post(
#     "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token",
#     data=creds)
#
# post_json = post.json()
# access_token = post_json["access_token"]
# refresh_token = post_json["refresh_token"]
# # print(f"{access_token}\n{refresh_token}")


def title_search(title="Chainsaw Man"):
    base_url = "https://api.mangadex.org"

    r = requests.get(
        f"{base_url}/manga",
        params={"title": title}
    )
    search_results = [manga["id"] for manga in r.json()["data"]]
    return search_results


chainsaw_man = title_search()[0]


def language_filter(manga_id=chainsaw_man, languages="en"):
    base_url = "https://api.mangadex.org"

    r = requests.get(
        f"{base_url}/manga/{manga_id}/feed",
        params={"translatedLanguage[]": languages},
    )
    filtered_by_lang = [chapter["id"] for chapter in r.json()["data"]]
    return filtered_by_lang


if __name__ == "__main__":
    print(title_search()[0])
    print(language_filter())
