import os
import pytesseract

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar


class Reader:
    """Reads through permitted images in chosen directory for text"""

    def __init__(self, filepath=None):
        if filepath is None or filepath == "":
            self.filepath = "chainsaw-man-1.png"
        elif filepath is not None or filepath != "":
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

    def __init__(self, filepath, reader_results):
    # Create default filepath value if parameter left blank
        if filepath == "":
            self.filepath = "reader_results"
        else:
            self.filepath = filepath

        self.reader_results = reader_results

    def file_generator(self, filename=None):
    # Creates default filename value if parameter left blank
        if filename is None or filename == "":
            filename = "results"
        elif filename is not None or filename != "":
            filename = filename

        elif not os.path.exists(self.filepath):
            os.makedirs(self.filepath)

        with open(f"{self.filepath}/{filename}.txt", "w") as file:
            for line in self.reader_results:
                file.write(line)
            file.close()


if __name__ == "__main__":
    read_path = input("Enter a directory to scan images from: ")
    write_path = input("Enter a directory to write extracted text to: ")
    text_file = input("Enter a name for your file: ")
    # test_read = "D:/Projects/personal_projects/chainsaw-ocr"
    # test_write = "D:/Projects/personal_projects/chainsaw-ocr"

    pic_path = Path(read_path)
    reader = Reader(filepath=pic_path)
    reader.image_reader()
    writer = Writer(write_path, reader.results)
    writer.file_generator()
