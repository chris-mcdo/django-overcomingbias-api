import datetime
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from obapi.export import (EPUBPandocWriter, MarkdownPandocWriter,
                          export_sequence)
from obapi.models import ContentItem


@pytest.fixture
def alice():
    return User.objects.create_user("Alice", "alice@example.com", "alicepassword")


@pytest.fixture
def simple_sequence(alice):
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

    return seq


@pytest.mark.django_db
class TestExport:
    def test_export_simple_sequence_to_markdown(self, simple_sequence):
        # Arrange
        md_writer = MarkdownPandocWriter()
        md_writer.set_output_file(
            path_without_extension=Path("output", "test_sequence_simple")
        )

        # Act
        export_sequence(simple_sequence, md_writer)

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

        random_sequence = alice.sequences.create(title="Random Sequence")
        random_sequence.items.set(content)

        epub_writer = EPUBPandocWriter()
        epub_writer.set_output_file(
            path_without_extension=Path("output", "test_sequence_random")
        )

        # Act
        export_sequence(random_sequence, epub_writer)

    def test_export_obcontent_sequence(self, alice, random_obcontentitems):
        content = random_obcontentitems(10)

        obcontent_seq = alice.sequences.create(title="OB Sequence")
        obcontent_seq.items.set(content)

        epub_writer = EPUBPandocWriter()
        epub_writer.set_output_file(
            path_without_extension=Path("output", "test_sequence_ob")
        )

        # Act
        export_sequence(obcontent_seq, epub_writer)
