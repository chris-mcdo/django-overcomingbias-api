import pytest
from obapi.utils import parse_duration, plaintext_to_html


class TestParseDuration:
    def test_gives_correct_result_for_valid_durations(self):
        assert parse_duration("PT10S").total_seconds() == pytest.approx(10)
        assert parse_duration("P3DT3H5M2S").total_seconds() == pytest.approx(270302)

    def test_raises_error_for_invalid_durations(self):
        with pytest.raises(ValueError):
            parse_duration("arbitrary string")

        with pytest.raises(ValueError):
            parse_duration("PT3.827M")


class TestPlaintextToHTML:
    def test_removes_malicious_text(self):
        # Arrange
        malicious_text = "A text with an evil <script></script>"
        # Act
        html_text = plaintext_to_html(malicious_text)
        # Assert
        assert "<script>" not in html_text

    def test_linkifies_urls(self):
        text_with_url = "A www.example.com URL"
        html_text = plaintext_to_html(text_with_url)
        assert "</a>" in html_text

    def test_wraps_with_pre_tag(self):
        text = "Some sample text to be wrapped with pre tags"
        html_text = plaintext_to_html(text)
        assert html_text.startswith("<pre>")
        assert html_text.endswith("</pre>")
