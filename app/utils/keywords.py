import unicodedata
from typing import Generator, Iterator, List


def normalize_keywords(keywords: [Iterator[str], List[str]]) -> Iterator[str]:
    """
    Normalize keywords.
    :param keywords: an iterator or list of keywords
    :return: an interator of normalized keywords
    """
    return map(
        lambda k: unicodedata.normalize("NFD", k.lower().strip())
        .encode(encoding="ascii", errors="ignore")
        .decode(encoding="utf-8"),
        keywords,
    )


def split_keywords_generator(keywords_string: str) -> Generator[str, str, None]:
    """
    Create a generator that splits a string given multiple separators and yield only unique value.
    :param keywords_string: The keywords to split
    :return: A generator that yield each keyword
    """
    size = len(keywords_string)
    last = 0
    separators = {" ", ","}
    seen = set()
    for i in range(0, size):
        if keywords_string[i] in separators:
            if i - last > 1:  # Avoid the case of separators that follow each other
                word = keywords_string[last:i]
                if word not in seen:  # Don't yield a keyword already yielded
                    seen.add(word)
                    yield word
            last = min(i + 1, size)  # Avoid an OOB
        elif i + 1 == size:  # Return the last word if not a separator
            yield keywords_string[last:size]
