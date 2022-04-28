import datetime
import re

import bleach
from slugify import slugify

ISO_8601_DURATION_PATTERN = re.compile(
    (
        r"^P"  # starts with a P
        r"((?P<days>\d+)D)?"  # optional day field must come before T
        r"(T(?=\d+[HMS])((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?)?"
        r"$"
    )
)

SLUG_MAX_LENGTH = 100


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


def to_slug(text):
    return slugify(text, max_length=SLUG_MAX_LENGTH)
