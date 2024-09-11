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

            for index, file in enumerate(self.filepath.glob("*")):
                progress_bar(index, file_counter)

                # Parse through directory for images and add text to results
                try:
                    text = pytesseract.image_to_string(Image.open(file))
                    if text:
                        self.results.append(f"{file}:\n{text}")

                except (PermissionError, Image.UnidentifiedImageError):
                    continue

            extracted_text = [result for result in self.results]
            return extracted_text

        except (FileNotFoundError, NotADirectoryError):
            print("This directory does not exist.")


class Writer:

    def __init__(self, filepath, results):
        self.filepath = filepath
        self.results = results

    def doc_writer(self, filename):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        with open(f"{self.filepath}/{filename}", "w") as file:
            for line in self.results:
                file.write(line)
            file.close()


if __name__ == "__main__":
    # prompt = input("Please enter a directory: ")
    test_read = "C:/Users/oreng/Pictures/"
    test_write = "D:/Projects/personal_projects/chainsaw-ocr"
    test_name = "test"
    pic_path = Path(test_read)

    reader = Reader(filepath=pic_path)
    reader.image_reader()
    writer = Writer(test_write, reader.image_reader())
    writer.doc_writer("test.txt")
