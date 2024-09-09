import os
import pytesseract

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar


class Reader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.results = []

    def progress(self, count=0, file_counter=0):
        for self.file in os.listdir(self.filepath):
            file_counter = file_counter + 1
        return progress_bar(count, file_counter)

    def image_reader(self):
        for index, file in enumerate(self.filepath.glob("*")):
            try:
                text = pytesseract.image_to_string(Image.open(file))
                if text:
                    self.results.append(f"{file}:\n{text}")
            except (PermissionError, Image.UnidentifiedImageError):
                continue
            self.progress(index)
        [print(f"\n{result}") for result in self.results]


if __name__ == "__main__":
    pic_path = Path("C:/Users/oreng/Pictures")
    reader = Reader(filepath=pic_path)
    reader.progress()
    reader.image_reader()
