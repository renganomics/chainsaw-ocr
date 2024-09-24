class MangaDexRequests:

    BASE_URL = ...
    def __init__(self, title, language):
        self.title = title
        self.language = language

    def get_page_metadata(self, chapter_id):
        pass

    def download_url(self, image_url, filepath):
        pass

class Database:

    def __init__(self, cursor):
        self.cursor = cursor

    def create_table(self, name, columns):
        pass

    def insert_data(self, table, columns, values, data):
        pass


class PageUrls(Database):

    def retrieve_chapter_ids(self, table, columns):
        pass

    def create_table(self, name, columns):
        pass

    def insert_data(self, table, columns, values, data):
        pass


class ImageReader:

    def __init__(self, filepath):
        self.filepath = filepath

    def extract_text(self, page):
        pass

    def store_text(self, results):
        pass
