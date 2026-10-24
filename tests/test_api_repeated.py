from datetime import datetime, timezone

from django.test import TestCase
from ninja.testing import TestClient

from obapi.api import api
from obapi.models import YoutubeContentItem


class TestRepeatedContentLists(TestCase):
    def test_list_endpoints_remain_usable_across_requests(self):
        item = YoutubeContentItem.objects.create(
            item_id="abcdefghijk",
            title="Synthetic video",
            publish_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
            yt_channel_id="synthetic-channel",
            yt_channel_title="Synthetic channel",
        )
        client = TestClient(api)
        paths = [
            "/content/list/recent?count=1",
            "/content/list/all",
            "/content/list/date?after=2000-01-01T00:00:00Z&before=2030-01-01T00:00:00Z",
            "/content/list/recent?count=1",
        ]
        for path in paths:
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual([row["item_id"] for row in response.json()], [item.item_id])
