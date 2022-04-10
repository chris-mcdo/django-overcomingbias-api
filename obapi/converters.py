import re

from django.urls.converters import IntConverter, StringConverter


class ClassifierNameConverter(StringConverter):
    regex = r"(author|idea|topic)s"

    def to_python(self, value):
        return value.removesuffix("s")

    def to_url(self, value):
        return f"{value}s"


class YoutubeVideoIDConverter(StringConverter):
    regex = r"[0-9A-Za-z_-]{10}[048AEIMQUYcgkosw]"


class SpotifyEpisodeIDConverter(StringConverter):
    regex = r"[a-zA-Z0-9]{22}"


class OBPostNameConverter(StringConverter):
    regex = r"\d{4}/\d{2}/[a-z0-9-_%]+"


class OBPostNumberConverter(IntConverter):
    regex = r"[0-9]{5}"


class URLConverter:
    """Base class for converting between URLs and content IDs."""

    def to_id(self, value):
        return extract_pattern(self.regex, value)


class YoutubeVideoURLConverter(URLConverter):
    # Youtube video pattern: https://stackoverflow.com/a/37704433
    regex = (
        r"^(?:(?:https?:)?//)?(?:(?:www|m)\.)?(?:youtube(?:-nocookie)?\.com|youtu\.be)"
        r"/(?:[\w\-]+\?v=|embed/|v/)?"
        f"({YoutubeVideoIDConverter.regex})"
        r"\S*$"
    )

    def to_url(self, value):
        return f"https://www.youtube.com/watch?v={value}"


class SpotifyEpisodeURLConverter(URLConverter):
    regex = (
        r"^(?:(?:https?:)?//)?(?:open\.spotify\.com/episode/)"
        f"({SpotifyEpisodeIDConverter.regex})"
        r"\S*"
    )

    def to_url(self, value):
        return f"https://open.spotify.com/episode/{value}"


class OBPostLongURLConverter(URLConverter):
    regex = (
        r"^https?://www\.overcomingbias\.com/"
        f"({OBPostNameConverter.regex})"
        r"\.html$"
    )

    def to_url(self, value):
        return f"https://www.overcomingbias.com/{value}.html"


class OBPostShortURLConverter(URLConverter):
    regex = (
        r"^https?://www\.overcomingbias\.com/\?p="
        f"({OBPostNumberConverter.regex})"
        r"$"
    )

    def to_url(self, value):
        return f"https://www.overcomingbias.com/?p={value}"


def extract_pattern(pattern, string, group=1):
    """Extract a pattern from a string or raise error.

    Parameters
    ----------
    pattern : str
        Regular expression pattern to match.
    string : str
        String to extract the match from.
    group : int
        Number of the group to extract the match from.

    Returns
    -------
    str
        The value of the match.

    Raises
    ------
    ValueError
        If no match is found.
    """
    match = re.search(pattern, string)
    if match is None:
        raise ValueError("No match found.")

    match_string = match.group(group)
    return match_string
