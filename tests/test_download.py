import pytest
from obapi.download import (
    _get_spotify_api_token,
    download_essays,
    download_spotify_episodes_json,
    download_youtube_videos_json,
)
from obapi.exceptions import APICallError

from markers import require_spotify_api_auth, require_youtube_api_key


@require_youtube_api_key
class TestDownloadYoutubeVideosJSON:
    def test_no_error_raised_for_invalid_video_ids(self):
        result = download_youtube_videos_json(video_ids=["123"])
        assert isinstance(result, dict)

    def test_raises_error_for_invalid_api_key(self, settings):
        # Arrange
        settings.YOUTUBE_API_KEY = "FakeValue"

        # Act & assert
        with pytest.raises(APICallError):
            download_youtube_videos_json(video_ids=["C-gEQdGVXbk"])

    def test_works_correctly_for_valid_inputs(self):
        # Act
        test_video = download_youtube_videos_json(video_ids=["C-gEQdGVXbk"])

        # Assert
        assert "items" in test_video
        assert (
            test_video["items"][0]["snippet"]["title"]
            == "10 Python Tips and Tricks For Writing Better Code"
        )


@require_spotify_api_auth
class TestDownloadSpotifyEpisodesJSON:
    def test_raises_error_for_invalid_episode_ids(self):
        with pytest.raises(APICallError):
            download_spotify_episodes_json(episode_ids=["123"])

    def test_raises_error_for_invalid_user_credentials(self, settings):
        _get_spotify_api_token.cache_clear()
        settings.SPOTIFY_CLIENT_ID = "fake-id"
        with pytest.raises(APICallError):
            download_spotify_episodes_json(episode_ids=["6MAszRR6tdDnMsjgVdw4Jh"])

        settings.SPOTIFY_CLIENT_SECRET = "d7JxFQUjNMCBn6agfBtWfnM6BcioGowC"
        with pytest.raises(APICallError):
            download_spotify_episodes_json(episode_ids=["6MAszRR6tdDnMsjgVdw4Jh"])

    def test_returns_none_for_nonexistent_episodes(self):
        # Act
        non_episode = download_spotify_episodes_json(["6MAszRR6tdDnMsjgVdw4Jp"])
        # Assert
        assert non_episode["episodes"] == [None]

    def test_works_correctly_for_valid_inputs(self):
        # Act
        test_episode = download_spotify_episodes_json(
            episode_ids=["6MAszRR6tdDnMsjgVdw4Jh"]
        )
        # Assert
        assert "episodes" in test_episode
        assert (
            test_episode["episodes"][0]["show"]["publisher"]
            == "Mercatus Center at George Mason University"
        )


class TestDownloadEssay:
    def test_raises_error_for_invalid_essay_id(self):
        with pytest.raises(APICallError):
            download_essays(essay_ids=["blah"])

    def test_works_correctly_for_valid_inputs(self):
        # Act
        test_essay_id = "Varytax"
        test_essay = download_essays(essay_ids=[test_essay_id])[test_essay_id]
        # Assert
        assert isinstance(test_essay, str)
        assert len(test_essay) > 0
