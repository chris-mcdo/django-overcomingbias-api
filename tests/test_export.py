import datetime
from random import shuffle

import pytest
from django.contrib.auth.models import User
from obapi.models import ContentItem


@pytest.fixture
def alice():
    return User.objects.create_user("Alice", "alice@example.com", "alicepassword")


@pytest.mark.django_db
class TestExport:
    def test_export_simple_sequence_to_markdown(self, alice):
        # Arrange
        now = datetime.datetime.now()
        item_1 = ContentItem.objects.create(
            title="Item 1",
            description_html="<p>Item 1</p><p>Has 2 paragraphs</p>",
            publish_date=now,
        )
        item_2 = ContentItem.objects.create(
            title="Item 2",
            description_html="<p>Item 2</p><p>Has</p><p>3 paragraphs</p>",
            publish_date=now,
        )

        seq = alice.sequences.create(title="Simple Sequence")
        seq.items.add(item_1, item_2)

        # Act
        seq.export(output_file="output/test_sequence_simple.md")

    def test_export_random_sequence(
        self,
        alice,
        random_obcontentitems,
        random_youtubecontentitems,
        random_spotifycontentitems,
    ):
        # Arrange
        content = [
            *random_youtubecontentitems(5),
            *random_spotifycontentitems(5),
            *random_obcontentitems(5),
        ]
        shuffle(content)

        seq = alice.sequences.create(title="Random Sequence")
        seq.items.set(content)

        # Act
        seq.export(output_format="epub", output_file="output/test_sequence_random.epub")

    def test_export_obcontent_sequence(self, alice, random_obcontentitems):
        content = random_obcontentitems(10)

        seq = alice.sequences.create(title="OB Sequence")
        seq.items.set(content)

        # Act
        seq.export(output_format="epub", output_file="output/test_sequence_ob.epub")
