import os

from tqdm import tqdm

from database import Database
from imagereader import ImageReader
from mangadex import MangaDexRequests

if __name__ == "__main__":
    mdx = MangaDexRequests()
    mdx.get_manga_data(title="chainsaw man", languages="en")

    test_directory = "test"
    db = Database(test_directory)
    db.create_table(
        name="chapters",
        columns="volume_number INTEGER,"
        "chapter_number INTEGER,"
        "title TEXT,"
        "chapter_id TEXT,"
        "chapter_link TEXT",
    )

    # Iterate over chapter attributes and insert relevant data
    for index, chapter in enumerate(mdx.chapter_data["attributes"]):
        db.insert_data(
            table="chapters",
            columns="volume_number,chapter_number,title,chapter_id,chapter_link",
            data=(
                chapter["volume"],
                chapter["chapter"],
                chapter["title"],
                mdx.chapter_data["id"][index],
                f"https://mangadex.org/chapter/{mdx.chapter_data['id'][index]}",
            ),
        )

    chapters_db = db.retrieve_data(table="chapters", columns="*")

    db.create_table(
        name="page_links",
        columns="volume_number INTEGER,"
        "chapter_number INTEGER,"
        "title TEXT,"
        "page_number INTEGER,"
        "link TEXT",
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
                columns="volume_number,chapter_number,title,page_number,link",
                data=(volume_number, chapter_number, chapter_title, index + 1, url),
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
                filename=f"page_{page_number}",
            )
    else:
        print(f"parent directory {image_download_dir} already exists")

    image_directory = "test_download"
    img = ImageReader()
    img.scan_folder(image_directory)
    image_list = img.png_list

    for png in tqdm(image_list[5]):
        png_text = img.extract_text(png)
        img.store_text(results=png_text, filepath=png)
