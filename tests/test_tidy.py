import datetime

import pytest
from obapi.download import (
    download_essays,
    download_spotify_episodes_json,
    download_youtube_videos_json,
)
from obapi.tidy import (
    _tidy_ob_post_html,
    _tidy_ob_post_object,
    _tidy_spotify_episode_json,
    _tidy_youtube_video_json,
    tidy_essays,
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


class TestTidyOBPostHTML:
    @pytest.fixture
    def wrap(self):
        """Wrap a string in HTML tags, to make it look like a post."""

        def _wrap(body):
            return f'<div class="entry-content">{body}</div>'

        return _wrap

    @pytest.mark.parametrize(
        "original,expected",
        [
            ("<p>systems with impressive</p>", "<p>systems with impressive</p>"),
            (
                (
                    "<p>Nonsense string <em>with</em> many nbsps.</p>"
                    "<p> Continues over 2 paragraphs in one string.</p>"
                ),
                (
                    "<p>Nonsense string <em>with</em> many nbsps.</p>"
                    "<p> Continues over 2 paragraphs in one string.</p>"
                ),
            ),
        ],
    )
    def test_replaces_nbsp(self, wrap, original, expected):
        assert _tidy_ob_post_html(wrap(original)) == expected

    @pytest.mark.parametrize(
        "original,expected",
        [
            ("<dl><dd>Example</dd></dl>", "<blockquote><p>Example</p></blockquote>"),
            (
                '<dl style="margin-left: 40px;"><dd>Example</dd></dl>',
                "<blockquote><p>Example</p></blockquote>",
            ),
            (
                "<dl><dd>Example 1</dd><dd>Example 2</dd></dl>",
                "<blockquote><p>Example 1</p><p>Example 2</p></blockquote>",
            ),
            (
                '<p style="padding-left: 30px;">A short string</p>',
                "<blockquote><p>A short string</p></blockquote>",
            ),
            (
                '<div class="blockquote" style="margin-left: 40px;">Values</div>',
                "<blockquote><p>Values</p></blockquote>",
            ),
            (
                '<div class="blockquote">Example</div>',
                "<blockquote><p>Example</p></blockquote>",
            ),
            (
                '<div style="margin-left: 40px;">Example</div>',
                "<blockquote><p>Example</p></blockquote>",
            ),
            (
                '<p style="margin-left: 40px;">Example</p>',
                "<blockquote><p>Example</p></blockquote>",
            ),
            (
                '<p style="padding-left: 30px; text-align: center;">T<sub>ij</sub></p>',
                "<blockquote><p>T<sub>ij</sub></p></blockquote>",
            ),
            (
                '<p style="padding-left: 40px;">Example</p>',
                "<blockquote><p>Example</p></blockquote>",
            ),
            (
                '<p style="padding-left: 37px;">Example</p>',
                '<p style="padding-left: 37px;">Example</p>',
            ),
        ],
    )
    def test_converts_single_blockquotes(self, wrap, original, expected):
        assert _tidy_ob_post_html(wrap(original)) == expected

    @pytest.mark.parametrize(
        "original,expected",
        [
            (
                '<p style="padding-left: 60px;">Example</p>',
                "<blockquote><blockquote><p>Example</p></blockquote></blockquote>",
            )
        ],
    )
    def test_converts_double_blockquotes(self, wrap, original, expected):
        assert _tidy_ob_post_html(wrap(original)) == expected

    def test_unwraps_apple_space(self, wrap):
        original = '<p>Example.<span class="Apple-converted-space"> </span></p>'
        expected = "<p>Example. </p>"
        assert _tidy_ob_post_html(wrap(original)) == expected

    def test_removes_msonormal_attributes(self, wrap):
        original = '<p class="MsoNormal">Example</p>'
        expected = "<p>Example</p>"
        assert _tidy_ob_post_html(wrap(original)) == expected

    def test_removes_nobr_tags(self, wrap):
        original = "<p>Example<nobr></nobr><strong><nobr></nobr> </strong></p>"
        expected = "<p>Example<strong> </strong></p>"
        assert _tidy_ob_post_html(wrap(original)) == expected


class TestTidyEssay:
    def test_returns_expected_result_for_example_essay(self):
        # Arrange
        essay_id = "Varytax"
        raw_essays = download_essays([essay_id])

        # Act
        tidied_essays = tidy_essays([essay_id], raw_essays)

        essay = tidied_essays[0]

        # Assert
        assert essay["item_id"] == "Varytax"
        assert essay["title"] == "Diet Pork"
