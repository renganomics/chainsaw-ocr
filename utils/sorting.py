import re


def parse_chapter_number(chapter_str: str) -> float | None:
    try:
        return float(chapter_str)
    except (TypeError, ValueError):
        return None


def natural_sort_key(filename):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", filename)
    ]


def filter_chapters_by_range(chapters, start: float, end: float):
    selected = []

    for chapter in chapters:
        num = parse_chapter_number(chapter["chapter"])

        if num is None:
            continue

        if start <= num <= end:
            selected.append(chapter)

    return selected
