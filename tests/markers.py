import pytest
from django.conf import settings

require_youtube_api_key = pytest.mark.skipif(
    settings.YOUTUBE_API_KEY is None,
    reason="Requires a valid YouTube API key to be set.",
)

require_spotify_api_auth = pytest.mark.skipif(
    settings.SPOTIFY_CLIENT_ID is None and settings.SPOTIFY_CLIENT_SECRET is None,
    reason="Requires a valid Spotify client ID and secret to be set.",
)
