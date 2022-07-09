import re

YOUTUBE_VIDEO_ID_REGEX = r"[0-9A-Za-z_-]{10}[048AEIMQUYcgkosw]"
SPOTIFY_EPISODE_ID_REGEX = r"[a-zA-Z0-9]{22}"
OB_POST_NAME_REGEX = r"\d{4}/\d{2}/[a-z0-9-_%]+"
OB_POST_NUMBER_REGEX = r"[0-9]{5}"
ESSAY_ID_REGEX = r"[a-zA-Z0-9-_%]+"


class URLConverter:
    """Base class for converting between URLs and content IDs."""

    def to_id(self, value, group=1):
        # Extract first matching group of regex pattern by default
        match = re.search(self.regex, value)
        if match is None:
            raise ValueError("No match found.")
        item_id = match.group(group)

        return item_id


class YoutubeVideoURLConverter(URLConverter):
    # Youtube video pattern: https://stackoverflow.com/a/37704433
    regex = (
        r"(?:(?:https?:)?//)?(?:(?:www|m)\.)?(?:youtube(?:-nocookie)?\.com|youtu\.be)"
        r"/(?:[\w\-]+\?v=|embed/|v/)?"
        f"({YOUTUBE_VIDEO_ID_REGEX})"
        r"\S*"
    )

    def to_url(self, value):
        return f"https://www.youtube.com/watch?v={value}"


class SpotifyEpisodeURLConverter(URLConverter):
    regex = (
        r"(?:(?:https?:)?//)?(?:open\.spotify\.com/episode/)"
        f"({SPOTIFY_EPISODE_ID_REGEX})"
        r"\S*"
    )

    def to_url(self, value):
        return f"https://open.spotify.com/episode/{value}"


class OBPostLongURLConverter(URLConverter):
    regex = (
        rf"(?:https?://)?(?:www\.)?overcomingbias\.com/({OB_POST_NAME_REGEX})\.html?"
    )

    def to_url(self, value):
        return f"https://www.overcomingbias.com/{value}.html"


class OBPostShortURLConverter(URLConverter):
    regex = (
        r"(?:https?://)?(?:www\.)?overcomingbias\.com/\?p=" f"({OB_POST_NUMBER_REGEX})"
    )

    def to_url(self, value):
        return f"https://www.overcomingbias.com/?p={value}"


class EssayURLConverter(URLConverter):
    regex = (
        r"(?:https?://)"
        r"(?:mason\.gmu\.edu/~rhanson|hanson\.gmu\.edu)"
        rf"/({ESSAY_ID_REGEX})\.html?"
        r"\S*"
    )

    def to_url(self, value):
        return f"https://mason.gmu.edu/~rhanson/{value}.html"
