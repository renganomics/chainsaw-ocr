import os

import pytesseract
from PIL import Image, ImageOps


class ImageReader:
    """Handles Tesseract-OCR and file interactions"""

    def __init__(self):
        self.png_list = []

    def scan_folder(self, parent):
        # Iterate over files in parent directory for png files
        for file in os.listdir(parent):
            if file.endswith(".png"):
                self.png_list.append(f"{parent}/{file}")
            else:
                # Add file to path
                current_path = "".join((parent, "/", file))
                # Call method for every subdirectory if it is a folder
                if os.path.isdir(current_path):
                    ImageReader.scan_folder(self, parent=current_path)
        return self.png_list

    @staticmethod
    def extract_text(image_path, scale_factor=3):
        # Turn image greyscale to improve readability
        with Image.open(image_path, mode="r") as image:
            grey_image = ImageOps.grayscale(image)

            # Resize image to improve readability
            resized_image = grey_image.resize(
                (grey_image.width * scale_factor, grey_image.height * scale_factor),
                resample=Image.Resampling.LANCZOS,
            )
            # Extract text and store as string
            _extracted_text = pytesseract.image_to_string(resized_image)
        return _extracted_text

    @staticmethod
    def store_text(results, filepath):
        # Remove png property from file
        storage_path = f"text_results/{filepath.replace('.png', '')}"
        # Separate directories from filename
        head, sep, tail = storage_path.partition("page_")

        try:
            # Create filepath if non-existent
            if not os.path.exists(storage_path):
                os.makedirs(head)
            else:
                print("filepath already exists")
        except FileExistsError:
            # Rejoin storage_path elements and write results as txt file
            with open(f"{head}/{sep}{tail}.txt", "w") as file:
                file.write(results)
