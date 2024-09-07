import os
import pytesseract

from PIL import Image
from pathlib import Path
from progress_bar import progress_bar

filepath = Path("C:/Users/oreng/Pictures")

results = []

file_counter = 0
for file in os.listdir(filepath):
    file_counter = file_counter + 1

progress_bar(0, file_counter)

for index, file in enumerate(filepath.glob("*")):
    try:
        text = pytesseract.image_to_string(Image.open(file))
        if text:
            results.append(f"{file}:\n{text}")
    except (PermissionError, Image.UnidentifiedImageError):
        continue
    progress_bar(index, file_counter)

[print(f"\n{result}") for result in results]
