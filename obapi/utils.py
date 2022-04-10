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


def parse_duration(duration):
    if (components := ISO_8601_DURATION_PATTERN.search(duration)) is None:
        raise ValueError(f'"{duration}" is not a valid ISO-8601 duration.')
    components = {
        k: int(v if v is not None else 0) for k, v in components.groupdict().items()
    }
    return datetime.timedelta(**components)


def plaintext_to_html(text):
    # Convert line breaks to <br> elements
    broken_text = text.replace("\n", "<br>")

    # Linkify URLs and email addresses
    return bleach.linkify(broken_text, parse_email=True)


def to_slug(text):
    return slugify(text)
