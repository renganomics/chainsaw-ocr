from services.mangadex import MangaDexRequests


def main():
    title = input("Please enter a manga title: ").strip()
    language = input("Please enter a language: ").strip().lower() or "en"

    client = MangaDexRequests()
    results = client.search_manga(title, language)
    filtered = client.filter_by_language(results, language)

    if not filtered:
        print("No manga found in that language")
        return

    for i, manga in enumerate(filtered):
        print(f"{i + 1}: {manga['attributes']['title'][language]}")

    try:
        choice = int(input("Select manga: ")) - 1
        selected = filtered[choice]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    manga_id = selected["id"]
    print(f"Manga ID: {manga_id}")

    # chapter_ids, attrs = client.get_chapters(title, "en")
    #
    # for chapter_id, attrs in tqdm(chapter_ids, total=len(chapter_ids)):
    #     folder = download_chapter(client, chapter_id, attrs)
    #
    #     if folder:
    #         create_cbz(folder)


if __name__ == "__main__":
    main()
