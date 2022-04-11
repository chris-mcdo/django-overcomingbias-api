import datetime

import pytest
from obapi.download import download_spotify_episodes_json, download_youtube_videos_json
from obapi.tidy import (
    _tidy_ob_post_object,
    _tidy_spotify_episode_json,
    _tidy_youtube_video_json,
)
from obscraper import get_post_by_url

from markers import require_spotify_api_auth, require_youtube_api_key


class TestTidyYoutubeVideoJSON:
    @require_youtube_api_key
    def test_returns_expected_result_for_example_videos(self):
        # Arrange
        tricks_response = download_youtube_videos_json(["C-gEQdGVXbk"])

        # Act
        tricks_json = _tidy_youtube_video_json(tricks_response["items"][0])

        # Assert
        assert (
            tricks_json["title"] == "10 Python Tips and Tricks For Writing Better Code"
        )
        assert tricks_json["duration"].total_seconds() == pytest.approx(2361)
        assert tricks_json["yt_description"].startswith("This video is")

        # Arrange
        trends_response = download_youtube_videos_json(["e6LOWKVq5sQ"])

        # Act
        trends_json = _tidy_youtube_video_json(trends_response["items"][0])

        # Assert
        assert trends_json["yt_description"] == ""
        assert set(trends_json["classifier_names"]) == {"simpsons", "disco stu"}
        assert trends_json["author_names"] == ["dumbmatter"]


class TestTidySpotifyEpisodeJSON:
    @require_spotify_api_auth
    def test_returns_expected_result_for_example_episode(self):
        # Arrange
        signals_response = download_spotify_episodes_json(["6MAszRR6tdDnMsjgVdw4Jh"])

        # Act
        signals_json = _tidy_spotify_episode_json(signals_response["episodes"][0])

        # Assert
        assert (
            signals_json["title"]
            == "Robin Hanson on Signaling and Self-Deception (Live at Mason Econ)"
        )
        assert signals_json["sp_show_title"] == "Conversations with Tyler"
        assert signals_json["sp_description"].startswith(
            "If intros aren’t about introductions"
        )


class TestTidyOBPostObject:
    def test_returns_expected_result_for_example_post(self):
        # Arrange
        post_raw = get_post_by_url(
            "https://www.overcomingbias.com/2009/03/signaling-in-economics.html"
        )

        # Act
        post_tidy = _tidy_ob_post_object(post_raw)

        # Assert
        assert post_tidy["title"] == "Signaling in Economics"
        assert post_tidy["publish_date"] == datetime.datetime(
            2009, 3, 21, 22, 0, tzinfo=datetime.timezone.utc
        )
        assert post_tidy["ob_post_number"] == 16642
        assert post_tidy["text_plain"].startswith("Arnold Kling cites this")
