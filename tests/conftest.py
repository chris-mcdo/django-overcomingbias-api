import datetime
import random
from dataclasses import replace

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


@pytest.fixture
def legacy_ob_posts(monkeypatch):
    """Synthetic scraper responses; the legacy WordPress source is retired.

    Patch only the download boundary. Assembly, tidying, database updates and
    exports still use their real implementations. No live posts are fetched.
    """
    posts = {}
    for i in range(1, 13):
        timestamp = datetime.datetime(2020, 1, i, tzinfo=datetime.timezone.utc)
        post = obscraper.Post(
            name=f"2020/01/synthetic-post-{i:02d}",
            number=10000 + i,
            page_type="post",
            page_status="publish",
            page_format="standard",
            title=f"Synthetic post {i}",
            author="Synthetic Author",
            publish_date=timestamp,
            tags=["synthetic"],
            categories=[],
            text_html='<div class="entry-content"><p>Synthetic post body.</p></div>',
            word_count=3,
            internal_links=[],
            external_links=[],
            disqus_id=None,
            votes=0,
            comments=0,
            edit_date=timestamp + datetime.timedelta(hours=1),
        )
        posts[post.name] = post

    monkeypatch.setattr(
        "obapi.download.get_edit_dates",
        lambda: {name: post.edit_date for name, post in posts.items()},
    )
    monkeypatch.setattr(
        "obapi.download.get_posts_by_names",
        lambda names: {name: replace(posts[name]) if name in posts else None for name in names},
    )
    return posts


@pytest.fixture
def obcontent_edit_dates(legacy_ob_posts):
    return {name: post.edit_date for name, post in legacy_ob_posts.items()}


@pytest.fixture
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
