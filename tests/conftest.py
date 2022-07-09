import random

import obscraper
import pytest
from obapi.models import OBContentItem
from obapi.models.content import (
    EssayContentItem,
    SpotifyContentItem,
    YoutubeContentItem,
)

from sample_data import SAMPLE_ESSAY_IDS, SAMPLE_SPOTIFY_IDS, SAMPLE_YOUTUBE_IDS


def create_random_items(sample_ids, n, model):
    sample_ids = random.sample(sample_ids, n)
    created_items = model.objects.create_items(sample_ids)
    return [item for item in created_items if item is not None]


@pytest.fixture(scope="session")
def obcontent_edit_dates():
    return obscraper.get_edit_dates()


@pytest.fixture(scope="session")
def random_obcontentitems(obcontent_edit_dates):
    """Factory function which populates the database with OvercomingBias posts."""

    def _random_obcontentitems(n):
        sample_ids = sorted(obcontent_edit_dates.keys())
        return create_random_items(sample_ids, n, OBContentItem)

    return _random_obcontentitems


@pytest.fixture(scope="session")
def random_youtubecontentitems():
    """Factory function which populates the database with YouTube videos."""

    def _random_youtubecontentitems(n):
        return create_random_items(SAMPLE_YOUTUBE_IDS, n, YoutubeContentItem)

    return _random_youtubecontentitems


@pytest.fixture(scope="session")
def random_spotifycontentitems():
    """Factory function which populates the database with Spotify episodes."""

    def _random_spotifycontentitems(n):
        return create_random_items(SAMPLE_SPOTIFY_IDS, n, SpotifyContentItem)

    return _random_spotifycontentitems


@pytest.fixture(scope="session")
def random_essaycontentitems():
    """Factory function which populates the database with Essays."""

    def _random_essaycontentitems(n):
        return create_random_items(SAMPLE_ESSAY_IDS, n, EssayContentItem)

    return _random_essaycontentitems
