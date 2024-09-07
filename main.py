import os
import PIL
import pytesseract
from threading import Thread

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar

filepath = Path("C:/Users/oreng/Pictures")

file_counter = 0
for file in os.listdir(filepath):
    file_counter = file_counter + 1

progress_bar(0, file_counter)

for index, file in enumerate(filepath.glob("*")):
    print(f"{file}")

    # folder_path = Path(f"C:/Users/oreng/Pictures/{file}").glob("*")
    # for folder_file in folder_path:
    #     try:
    #         print(pytesseract.image_to_string(Image.open(file)))
    #     except (PermissionError, PIL.UnidentifiedImageError):
    #         if PermissionError:
    #             print(f"There was a PermissionError for {file}.")
    #         if PIL.UnidentifiedImageError:
    #             print(f"There was an UnidentifiedImageError for {file}.\n")
    #     continue

    try:
        text = pytesseract.image_to_string(Image.open(file))
        print(text)
        progress_bar(index + 1, file_counter)

    except (PermissionError, PIL.UnidentifiedImageError):
        if PermissionError:
            print(f"There was a PermissionError for {file}.")
        if PIL.UnidentifiedImageError:
            print(f"There was an UnidentifiedImageError for {file}.\n")
        continue


