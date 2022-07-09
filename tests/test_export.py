import datetime

import pytest
from obapi.export import EPUBPandocWriter, MarkdownPandocWriter, export_sequence
from obapi.models import ContentItem, Sequence

from markers import require_spotify_api_auth, require_youtube_api_key


@pytest.fixture
def simple_sequence():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
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
    seq = Sequence.objects.create(title="Simple Sequence")
    seq.items.add(item_1, item_2)

    return seq


@pytest.mark.django_db
class TestExport:
    def test_export_simple_sequence_to_markdown(self, simple_sequence, tmp_path):
        # Arrange
        md_writer = MarkdownPandocWriter()
        md_writer.set_output_file(
            path_without_extension=tmp_path / "test_sequence_simple"
        )

        # Act
        export_sequence(simple_sequence, md_writer)

    @require_youtube_api_key
    @require_spotify_api_auth
    def test_export_random_sequence(
        self,
        random_obcontentitems,
        random_youtubecontentitems,
        random_spotifycontentitems,
        random_essaycontentitems,
        tmp_path,
    ):
        # Arrange
        content = [
            *random_youtubecontentitems(5),
            *random_spotifycontentitems(5),
            *random_obcontentitems(5),
            *random_essaycontentitems(5),
        ]

        random_sequence = Sequence.objects.create(title="Random Sequence")
        random_sequence.items.set(content)

        epub_writer = EPUBPandocWriter()
        epub_writer.set_output_file(
            path_without_extension=tmp_path / "test_sequence_random"
        )

        # Act
        export_sequence(random_sequence, epub_writer)

    def test_export_obcontent_sequence(self, random_obcontentitems, tmp_path):
        content = random_obcontentitems(10)

        obcontent_seq = Sequence.objects.create(title="OB Sequence")
        obcontent_seq.items.set(content)

        epub_writer = EPUBPandocWriter()
        epub_writer.set_output_file(
            path_without_extension=tmp_path / "test_sequence_ob"
        )

        # Act
        export_sequence(obcontent_seq, epub_writer)
