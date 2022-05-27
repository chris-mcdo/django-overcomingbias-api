import django.db.models.deletion
import obapi.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name.", max_length=100, unique=True),
                ),
                (
                    "slug",
                    obapi.modelfields.SimpleSlugField(
                        editable=False, max_length=150, unique=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ContentItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_timestamp",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="creation date"
                    ),
                ),
                (
                    "update_timestamp",
                    models.DateTimeField(auto_now=True, verbose_name="update date"),
                ),
                (
                    "download_timestamp",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="download date"
                    ),
                ),
                (
                    "title",
                    models.CharField(help_text="Title of content.", max_length=100),
                ),
                (
                    "description_html",
                    models.TextField(
                        blank=True,
                        help_text="HTML description of content.",
                        max_length=5000,
                    ),
                ),
                (
                    "publish_date",
                    models.DateTimeField(help_text="Date of publication."),
                ),
                (
                    "edit_date",
                    models.DateTimeField(
                        blank=True, help_text="Date of last edit.", null=True
                    ),
                ),
                (
                    "authors",
                    models.ManyToManyField(
                        help_text="Authors.", related_name="content", to="obapi.author"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExternalLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.URLField(help_text="Link URL.", unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Idea",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name.", max_length=100, unique=True),
                ),
                (
                    "slug",
                    obapi.modelfields.SimpleSlugField(
                        editable=False, max_length=150, unique=True
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, help_text="Brief description.", max_length=100
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Sequence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(help_text="Sequence title.", max_length=100),
                ),
                (
                    "slug",
                    obapi.modelfields.SimpleSlugField(editable=False, max_length=150),
                ),
                (
                    "abstract",
                    models.TextField(
                        blank=True,
                        help_text="Description of sequence.",
                        max_length=5000,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name.", max_length=100, unique=True),
                ),
                (
                    "slug",
                    obapi.modelfields.SimpleSlugField(
                        editable=False, max_length=150, unique=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name.", max_length=100, unique=True),
                ),
                (
                    "slug",
                    obapi.modelfields.SimpleSlugField(
                        editable=False, max_length=150, unique=True
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, help_text="Brief description.", max_length=100
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AudioContentItem",
            fields=[
                (
                    "contentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.contentitem",
                    ),
                ),
                (
                    "duration",
                    models.DurationField(
                        blank=True, help_text="Duration of episode.", null=True
                    ),
                ),
                (
                    "listen_count",
                    models.PositiveIntegerField(
                        blank=True, help_text="Number of episode listens.", null=True
                    ),
                ),
            ],
            options={
                "verbose_name": "episode",
            },
            bases=("obapi.contentitem",),
        ),
        migrations.CreateModel(
            name="TextContentItem",
            fields=[
                (
                    "contentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.contentitem",
                    ),
                ),
                (
                    "word_count",
                    models.PositiveIntegerField(
                        blank=True, help_text="Word count.", null=True
                    ),
                ),
                (
                    "text_html",
                    models.TextField(
                        blank=True,
                        help_text="Content text HTML.",
                        verbose_name="content text HTML",
                    ),
                ),
                (
                    "text_plain",
                    models.TextField(
                        blank=True,
                        help_text="Content plaintext.",
                        verbose_name="content plaintext",
                    ),
                ),
            ],
            bases=("obapi.contentitem",),
        ),
        migrations.CreateModel(
            name="VideoContentItem",
            fields=[
                (
                    "contentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.contentitem",
                    ),
                ),
                (
                    "duration",
                    models.DurationField(
                        blank=True, help_text="Duration of video.", null=True
                    ),
                ),
                (
                    "view_count",
                    models.PositiveIntegerField(
                        blank=True, help_text="Number of video views.", null=True
                    ),
                ),
            ],
            options={
                "verbose_name": "video",
            },
            bases=("obapi.contentitem",),
        ),
        migrations.CreateModel(
            name="TopicAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    obapi.modelfields.SimpleSlugField(
                        help_text="Alias text.", max_length=150, unique=True
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="True for the alias which equals the owner name.",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Topic the alias refers to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        related_query_name="alias",
                        to="obapi.topic",
                        verbose_name="topic",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "aliases",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TagAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    obapi.modelfields.SimpleSlugField(
                        help_text="Alias text.", max_length=150, unique=True
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="True for the alias which equals the owner name.",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Tag the alias refers to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        related_query_name="alias",
                        to="obapi.tag",
                        verbose_name="tag",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "aliases",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SequenceMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name="order"
                    ),
                ),
                (
                    "content_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sequence_members",
                        related_query_name="sequence_members",
                        to="obapi.contentitem",
                    ),
                ),
                (
                    "sequence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        related_query_name="members",
                        to="obapi.sequence",
                    ),
                ),
            ],
            options={
                "ordering": ("sequence", "order"),
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="sequence",
            name="items",
            field=models.ManyToManyField(
                through="obapi.SequenceMember", to="obapi.contentitem"
            ),
        ),
        migrations.CreateModel(
            name="IdeaAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    obapi.modelfields.SimpleSlugField(
                        help_text="Alias text.", max_length=150, unique=True
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="True for the alias which equals the owner name.",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Idea the alias refers to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        related_query_name="alias",
                        to="obapi.idea",
                        verbose_name="idea",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "aliases",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="contentitem",
            name="external_links",
            field=models.ManyToManyField(
                blank=True,
                help_text="Links to external webpages.",
                related_name="content",
                related_query_name="content",
                to="obapi.externallink",
            ),
        ),
        migrations.AddField(
            model_name="contentitem",
            name="ideas",
            field=models.ManyToManyField(
                blank=True,
                help_text="Ideas discussed or referenced by the content.",
                related_name="content",
                related_query_name="content",
                to="obapi.idea",
            ),
        ),
        migrations.AddField(
            model_name="contentitem",
            name="internal_links",
            field=models.ManyToManyField(
                blank=True,
                help_text="Links to other content items.",
                related_name="internal_pingbacks",
                related_query_name="internal_pingbacks",
                to="obapi.contentitem",
            ),
        ),
        migrations.AddField(
            model_name="contentitem",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                help_text="Miscellaneous tags.",
                related_name="content",
                related_query_name="content",
                to="obapi.tag",
            ),
        ),
        migrations.AddField(
            model_name="contentitem",
            name="topics",
            field=models.ManyToManyField(
                blank=True,
                help_text="Topics discussed or references by the content.",
                related_name="content",
                related_query_name="content",
                to="obapi.topic",
            ),
        ),
        migrations.CreateModel(
            name="AuthorAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    obapi.modelfields.SimpleSlugField(
                        help_text="Alias text.", max_length=150, unique=True
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="True for the alias which equals the owner name.",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Author the alias refers to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        related_query_name="alias",
                        to="obapi.author",
                        verbose_name="author",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "aliases",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OBContentItem",
            fields=[
                (
                    "textcontentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.textcontentitem",
                    ),
                ),
                (
                    "item_id",
                    models.CharField(
                        help_text='Post string identifier. E.g. "2006/11/introduction"',
                        max_length=100,
                        unique=True,
                        verbose_name="string ID",
                    ),
                ),
                (
                    "ob_post_number",
                    models.PositiveIntegerField(
                        help_text="Post number identifier.",
                        unique=True,
                        verbose_name="number ID",
                    ),
                ),
                (
                    "disqus_id",
                    models.CharField(
                        blank=True,
                        help_text="Post Disqus API string identifier.",
                        max_length=200,
                    ),
                ),
                (
                    "ob_likes",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="Number of likes.",
                        null=True,
                        verbose_name="likes",
                    ),
                ),
                (
                    "ob_comments",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="Number of comments.",
                        null=True,
                        verbose_name="comments",
                    ),
                ),
            ],
            options={
                "verbose_name": "overcomingbias post",
            },
            bases=("obapi.textcontentitem",),
        ),
        migrations.CreateModel(
            name="SpotifyContentItem",
            fields=[
                (
                    "audiocontentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.audiocontentitem",
                    ),
                ),
                (
                    "item_id",
                    models.CharField(
                        help_text="Episode ID.",
                        max_length=30,
                        unique=True,
                        verbose_name="episode ID",
                    ),
                ),
                (
                    "sp_show_id",
                    models.CharField(
                        help_text="Show ID.", max_length=30, verbose_name="show ID"
                    ),
                ),
                (
                    "sp_show_title",
                    models.CharField(
                        help_text="Show title.",
                        max_length=200,
                        verbose_name="show title",
                    ),
                ),
                (
                    "sp_description",
                    models.TextField(
                        blank=True,
                        help_text="Episode description.",
                        max_length=5000,
                        verbose_name="description",
                    ),
                ),
            ],
            options={
                "verbose_name": "spotify episode",
            },
            bases=("obapi.audiocontentitem",),
        ),
        migrations.CreateModel(
            name="YoutubeContentItem",
            fields=[
                (
                    "videocontentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.videocontentitem",
                    ),
                ),
                (
                    "item_id",
                    models.CharField(
                        help_text="Video ID.",
                        max_length=30,
                        unique=True,
                        verbose_name="video ID",
                    ),
                ),
                (
                    "yt_channel_id",
                    models.CharField(
                        help_text="Channel ID.",
                        max_length=30,
                        verbose_name="channel ID",
                    ),
                ),
                (
                    "yt_channel_title",
                    models.CharField(
                        help_text="Channel title.",
                        max_length=30,
                        verbose_name="channel title",
                    ),
                ),
                (
                    "yt_likes",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Number of likes.",
                        null=True,
                        verbose_name="likes",
                    ),
                ),
                (
                    "yt_description",
                    models.TextField(
                        blank=True,
                        help_text="Video description.",
                        max_length=5000,
                        verbose_name="description",
                    ),
                ),
            ],
            options={
                "verbose_name": "youtube video",
            },
            bases=("obapi.videocontentitem",),
        ),
        migrations.AddConstraint(
            model_name="sequence",
            constraint=models.UniqueConstraint(
                fields=("slug",), name="unique_sequence_slug"
            ),
        ),
    ]
