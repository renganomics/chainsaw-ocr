import os
import pytesseract

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar


class Reader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.results = []

    def image_reader(self):
        """Loads progress bar while reading through permitted images in a
        directory"""
        try:
            # Get total file count of directory
            file_counter = 0
            for self.file in os.listdir(self.filepath):
                file_counter = file_counter + 1

            # Load progress bar with the loop index and total file count
            progress_bar(0, file_counter)
            for index, file in enumerate(self.filepath.glob("*")):
                progress_bar(index, file_counter)

                # Parse through directory for image files and scan for text
                try:
                    text = pytesseract.image_to_string(Image.open(file))
                    if text:
                        self.results.append(f"{file}:\n{text}")

                except (PermissionError, Image.UnidentifiedImageError):
                    continue

            [print(f"\n{result}") for result in self.results]

        except (FileNotFoundError, NotADirectoryError):
            print("This directory does not exist.")


if __name__ == "__main__":
    # prompt = input("Please enter a directory: ")
    test_path = "C:/Users/oreng/Pictures/"
    pic_path = Path(test_path)
    reader = Reader(filepath=pic_path)
    reader.image_reader()
