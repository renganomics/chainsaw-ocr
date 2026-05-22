from abc import ABC, abstractmethod


class Book(ABC):
    def __init__(self, title: str, author: str, publication_year: int):
        self._title = title
        self._author = author
        self._publication_year = publication_year

    def __str__(self) -> str:
        return f"{self._title} by {self._author} ({self._publication_year})"

    def get_title(self) -> str:
        return self._title

    def get_author(self) -> str:
        return self._author

    def get_publication_year(self) -> int:
        return self._publication_year

    @abstractmethod
    def get_book_type(self) -> str:
        return self.__class__.__name__


class Manga(Book):
    def __init__(
        self, title: str, author: str, publication_year: int, volume_count: int
    ) -> None:
        super().__init__(title, author, publication_year)
        self._volume_count = volume_count

    def get_volume_count(self) -> int:
        return self._volume_count

    def get_book_type(self) -> str:
        return "Manga"


if __name__ == "__main__":
    manga = Manga("One Piece", "Eiichiro Oda", 1997, 100)
    print(manga)
