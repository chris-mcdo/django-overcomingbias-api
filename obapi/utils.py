import datetime
import re

import bleach
import slugify

ISO_8601_DURATION_PATTERN = re.compile(
    (
        r"^P"  # starts with a P
        r"((?P<days>\d+)D)?"  # optional day field must come before T
        r"(T(?=\d+[HMS])((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?)?"
        r"$"
    )
)


def parse_duration(duration):
    if (components := ISO_8601_DURATION_PATTERN.search(duration)) is None:
        raise ValueError(f'"{duration}" is not a valid ISO-8601 duration.')
    components = {
        k: int(v if v is not None else 0) for k, v in components.groupdict().items()
    }
    return datetime.timedelta(**components)


def plaintext_to_html(text):
    """Clean and format plaintext, outputting HTML."""
    clean_text = bleach.clean(text)
    html_text = f"<pre>{clean_text}</pre>"
    linkified_text = bleach.linkify(html_text, parse_email=True)
    return linkified_text


def to_slug(text, max_length):
    return slugify.slugify(text, max_length=max_length)


def chunk_iterator(seq, chunk_size):
    """An iterator which yields chunks of size `chunk_size` of a sequence `seq`."""
    for i in range(0, len(seq), chunk_size):
        yield seq[i : i + chunk_size]


def count_words(text, ignore=None):
    """Count the number of words in a string, ignoring some."""
    if ignore is None:
        ignore = []
    text_without_punctuation = re.sub(r"[^a-zA-Z0-9\s]+", "", text)
    text_without_special_chars = re.sub(r"\s+", " ", text_without_punctuation)
    words = len(
        [word for word in str.split(text_without_special_chars) if word not in ignore]
    )
    return words
