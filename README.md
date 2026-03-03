# Chainsaw-OCR

Chainsaw-OCR is a Python command-line application that retrieves manga chapter
data via the MangaDex API, downloads associated page images, performs OCR text
extraction, and stores results for search and analysis.

This project was built to explore API interaction, database design, file system
automation, and OCR processing in a practical, end-to-end workflow.

## Features

- Retrieves structured chapter metadata via the MangaDex API
- Stores chapter and page data in an SQLite database
- Automates bulk image downloading and directory organisation
- Extracts text from images using OCR
- Designed for future expansion into searchable text queries

## Technologies Used

- Python
- SQLite
- MangaDex API
- Git
- Linux (developed and tested in Arch)

## Why Build This?

This project began as a curiosity-driven experiment and evolved into a hands-on
exercise in building a small data pipeline. The goal was to practice working
with external APIs, persistent data storage, file handling, and text extraction
within a command-line environment
