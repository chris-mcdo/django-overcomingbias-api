import pytest
from obapi.utils import parse_duration


class TestParseDuration:
    def test_gives_correct_result_for_valid_durations(self):
        assert parse_duration("PT10S").total_seconds() == pytest.approx(10)
        assert parse_duration("P3DT3H5M2S").total_seconds() == pytest.approx(270302)

    def test_raises_error_for_invalid_durations(self):
        with pytest.raises(ValueError):
            parse_duration("arbitrary string")

        with pytest.raises(ValueError):
            parse_duration("PT3.827M")
