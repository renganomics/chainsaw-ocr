import os
import zipfile
from utils.sorting import natural_sort_key


def create_cbz(chapter_folder: str) -> str:
    if not os.path.isdir(chapter_folder):
        raise FileNotFoundError(f"{chapter_folder} does not exist")

    cbz_path = f"{chapter_folder}.cbz"

    with zipfile.ZipFile(cbz_path, "w") as cbz:
        for file in sorted(os.listdir(chapter_folder), key=natural_sort_key):
            if file.endswith(".png"):
                full_path = os.path.join(chapter_folder, file)
                cbz.write(full_path, arcname=file)

    return cbz_path
