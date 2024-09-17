import os
import pytesseract

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar


class Reader:
    """Reads through permitted images in chosen directory for text"""

    def __init__(self, filepath: Path = "chainsaw-man-1.png"):
        self.filepath = filepath
        self.results = []

    def image_reader(self):
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

        except (FileNotFoundError, NotADirectoryError):
            print("This directory does not exist.")

        return self.results


class Writer:
    """Writes results of Reader class to text file of user's choice"""

    def __init__(self, reader_results: list[str],
                 filepath: str =f"{os.getcwd()}/reader_results"):

        if not os.path.exists(filepath):
            os.makedirs(filepath)
            os.chdir(filepath)
        self.filepath = filepath

        self.reader_results = reader_results

    def file_generator(self, filename: str = "results"):

        with open(f"{self.filepath}/{filename}.txt", "w") as file:
            for line in self.reader_results:
                file.write(line)
            file.close()

        print(f"Your file is stored in {self.filepath}/{filename}")


if __name__ == "__main__":
    read_path = Path(input("Enter a directory to scan images from: "))
    text_file = input("Enter a name for your file: ")

    reader = Reader(filepath=read_path)
    reader.image_reader()
    writer = Writer(reader.results)
    writer.file_generator(text_file)
