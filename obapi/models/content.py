from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from model_utils.managers import InheritanceQuerySet
from obapi import utils
from obapi.assemble import (
    assemble_essay_content_items,
    assemble_ob_content_items,
    assemble_ob_edit_dates,
    assemble_spotify_content_items,
    assemble_youtube_content_items,
)
from obapi.converters import (
    EssayURLConverter,
    OBPostLongURLConverter,
    OBPostShortURLConverter,
    SpotifyEpisodeURLConverter,
    YoutubeVideoURLConverter,
)
from obapi.models import (
    CLASSIFIER_SLUG_MAX_LENGTH,
    Author,
    ExternalLink,
    Idea,
    Tag,
    Topic,
)

DOWNLOAD_BATCH_SIZE = getattr(settings, "OBAPI_DOWNLOAD_BATCH_SIZE", 10000)


class ContentItemQuerySet(InheritanceQuerySet):
    """Custom QuerySet which can "assemble" and save objects."""

    # Converter from URLs to item IDs
    url_converters = ()

    def save_item(self, item=None, **kwargs):
        """Create a new item or update an existing item."""
        adding = item is None
        author_names = kwargs.pop("author_names", None)
        classifier_names = kwargs.pop("classifier_names", None)
        link_urls = kwargs.pop("link_urls", None)
        with transaction.atomic():
            # Update or create object
            if adding:
                item = self.create(**kwargs)
            else:
                for attr, value in kwargs.items():
                    setattr(item, attr, value)
                item.save()
            # Set ManyToMany related objects: authors, classifiers, links
            authors = self.get_or_create_authors_by_names(author_names)
            ideas, topics, tags = self.get_or_create_classifiers_by_names(
                classifier_names
            )
            external_links = self.get_or_create_external_links_by_urls(link_urls)
            relationship_attributes = {
                "authors": authors,
                "ideas": ideas,
                "topics": topics,
                "tags": tags,
                "external_links": external_links,
            }
            for attr, value in relationship_attributes.items():
                if value is not None:
                    # Clear old values, set new values
                    getattr(item, attr).set(value)
            # Only internalize links if some are added
            item.internalize_links(clear=external_links is not None)
        return item

    def get_or_create_authors_by_names(self, author_names):
        """Get or create a list of authors from some names."""
        if author_names is None:
            return None
        with transaction.atomic():
            # Match by alias
            authors = [
                Author.objects.get_or_create(
                    alias__text=utils.to_slug(
                        author_name, max_length=CLASSIFIER_SLUG_MAX_LENGTH
                    ),
                    defaults={"name": author_name},
                )
                for author_name in author_names
            ]
            return [author[0] for author in authors]

    def get_or_create_classifiers_by_names(self, classifier_names):
        """Get or create a list of ideas, topics and tags from some names."""
        if classifier_names is None:
            return None, None, None
        ideas = []
        topics = []
        tags = []
        with transaction.atomic():
            for classifier_name in classifier_names:
                # Match by alias
                query = Q(
                    alias__text=utils.to_slug(
                        classifier_name, max_length=CLASSIFIER_SLUG_MAX_LENGTH
                    )
                )
                try:
                    ideas.append(Idea.objects.get(query))
                    continue
                except Idea.DoesNotExist:
                    pass
                # If that fails, try to get topic with alias = classifier_name
                try:
                    topics.append(Topic.objects.get(query))
                    continue
                except Topic.DoesNotExist:
                    pass
                # If that fails, try to get a tag with alias = classifier_name
                # If no such tag exists, create a new one
                tags.append(
                    Tag.objects.filter(query).get_or_create(
                        defaults={"name": classifier_name},
                    )[0]
                )
        return ideas, topics, tags

    def get_or_create_external_links_by_urls(self, link_urls):
        if link_urls is None:
            return None
        url_max_length = ExternalLink._meta.get_field("url").max_length
        with transaction.atomic():
            return [
                ExternalLink.objects.get_or_create(url=link_url[:url_max_length])[0]
                for link_url in link_urls
            ]

    def assemble_items(self, item_ids=None):
        """Assemble items in QuerySet or from their item IDs."""
        if item_ids is None:
            # Construct item ids from QuerySet
            item_ids = [item.item_id for item in self]

        # Return if no IDs
        if item_ids == []:
            return []

        assembled_items = type(self).assemble_by_ids(item_ids)
        return assembled_items

    def create_item(self, item_id):
        """Create a single content item."""
        return self.create_items([item_id])[0]

    def create_items(self, item_ids):
        """Create items from their item IDs.

        Returns
        -------
        List[ContentItem | None]
        """
        # Assemble data
        assembled_items = self.assemble_items(item_ids)

        # Save items
        created_items = []
        with transaction.atomic():
            for item_data in assembled_items:
                if item_data is not None:
                    created_items.append(self.save_item(item=None, **item_data))
                else:
                    created_items.append(None)
        return created_items

    def bulk_create_items(self, item_ids, batch_size=DOWNLOAD_BATCH_SIZE):
        """Create items from their IDs, in batches.

        Returns
        -------
        The number of created items.
        """
        created_count = 0
        for item_ids_chunk in utils.chunk_iterator(item_ids, batch_size):
            created_items = self.create_items(item_ids_chunk)
            created_count += sum(item is not None for item in created_items)
        return created_count

    def update_items(self, exclude=None):
        """Update items in QuerySet, excluding certain fields.

        Returns
        -------
        List[Tuple[ContentItem, bool]]
            A list of tuples of the form (`item`, `updated`).
        """
        # Assemble data
        assembled_items = self.assemble_items()

        # Don't update excluded attributes
        if exclude is None:
            exclude = []
        for new_item in assembled_items:
            for attr in exclude:
                new_item.pop(attr, None)

        # Save items
        updated_items = []
        with transaction.atomic():
            for item, item_data in zip(self, assembled_items):
                if item_data is not None:
                    updated_item = self.save_item(item=item, **item_data)
                    updated_items.append((updated_item, True))
                else:
                    # Item assemble failed - return original item
                    updated_items.append((item, False))
        return updated_items

    def find_by_url(self, url):
        """Find a ContentItem by its URL.

        Raises
        ------
        ValueError
            If the URL does not match any recognised pattern.
        ContentItem.DoesNotExist
            If the URL matches a recognised pattern but no ContentItem is found.
        """
        # Try to use get_by_url for current class (if implemented)
        try:
            return self.get_by_url(url)
        except ValueError:
            # Don't catch Model.DoesNotExist
            pass

        # Otherwise try find_by_url methods of subclasses
        for model in self.model.__subclasses__():
            try:
                return model.objects.find_by_url(url)
            except ValueError:
                pass
            # Don't catch model.DoesNotExist
        raise ValueError  # URL did not match any ContentItem URL format

    def get_by_url(self, url):
        """Get a ContentItem by its URL.

        Raises
        ------
        ValueError
            If the URL does not match any content type.
        ContentItem.DoesNotExist
            If the URL matches a content type but no content item was found.
        """

        for converter, field in self.url_converters:
            try:
                item_id = converter.to_id(url)
            except ValueError:
                pass
            else:
                return self.get(**{field: item_id})
        raise ValueError(f"URL did not match any known format for type {type(self)}")

    def recent(self):
        """Return all content items sorted by publish date."""
        return self.order_by("-publish_date")


class ContentItem(models.Model):
    objects = ContentItemQuerySet.as_manager()

    create_timestamp = models.DateTimeField("creation date", auto_now_add=True)
    update_timestamp = models.DateTimeField(
        "update date",
        auto_now=True,
        help_text="When the item was last updated - either by hand or automatically.",
    )
    download_timestamp = models.DateTimeField(
        "download date",
        editable=False,
        null=True,
        help_text="When the item was last downloaded.",
    )

    title = models.CharField(max_length=200, help_text="Title of content.")
    description_html = models.TextField(
        max_length=5000, blank=True, help_text="HTML description of content."
    )
    publish_date = models.DateTimeField(help_text="Date of publication.")
    edit_date = models.DateTimeField(
        blank=True, null=True, help_text="Date of last edit."
    )
    authors = models.ManyToManyField(
        Author, related_name="content", help_text="Authors."
    )
    ideas = models.ManyToManyField(
        Idea,
        related_name="content",
        related_query_name="content",
        blank=True,
        help_text="Ideas discussed or referenced by the content.",
    )
    topics = models.ManyToManyField(
        Topic,
        related_name="content",
        related_query_name="content",
        blank=True,
        help_text="Topics discussed or references by the content.",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="content",
        related_query_name="content",
        blank=True,
        help_text="Miscellaneous tags.",
    )
    external_links = models.ManyToManyField(
        ExternalLink,
        related_name="content",
        related_query_name="content",
        blank=True,
        help_text="Links to external webpages.",
    )
    internal_links = models.ManyToManyField(
        "self",
        related_name="internal_pingbacks",
        related_query_name="internal_pingbacks",
        blank=True,
        help_text="Links to other content items.",
        symmetrical=False,
    )

    def __str__(self):
        return self.title

    @property
    def content_url(self):
        # Return URL of subclass
        return ContentItem.objects.get_subclass(pk=self.pk).content_url

    def get_absolute_url(self):
        return ContentItem.objects.get_subclass(pk=self.pk).get_absolute_url()

    def internalize_links(self, clear=False):
        """Try to make external links internal.

        Try to make external links internal by looking for the corresponding
        ContentItems.

        Parameters
        ----------
        clear : bool
            Whether to clear existing internal links.
        """
        if clear:
            self.internal_links.clear()
        for pk, url in self.external_links.values_list("pk", "url"):
            try:
                match = ContentItem.objects.find_by_url(url)
            except (ValueError, ContentItem.DoesNotExist):
                continue
            else:
                with transaction.atomic():
                    self.external_links.remove(pk)
                    self.internal_links.add(match)


class VideoContentItem(ContentItem):
    duration = models.DurationField(
        help_text="Duration of video.", blank=True, null=True
    )
    view_count = models.PositiveIntegerField(
        help_text="Number of video views.", blank=True, null=True
    )

    class Meta:
        verbose_name = "video"


class YoutubeContentItemQuerySet(ContentItemQuerySet):
    assemble_by_ids = assemble_youtube_content_items
    url_converters = ((YoutubeVideoURLConverter(), "item_id"),)


class YoutubeContentItem(VideoContentItem):
    objects = YoutubeContentItemQuerySet.as_manager()
    item_id = models.CharField(
        "video ID", max_length=30, unique=True, help_text="Video ID."
    )
    yt_channel_id = models.CharField(
        "channel ID", max_length=30, help_text="Channel ID."
    )
    yt_channel_title = models.CharField(
        "channel title", max_length=30, help_text="Channel title."
    )
    yt_likes = models.PositiveIntegerField(
        "likes", blank=True, null=True, help_text="Number of likes."
    )
    yt_description = models.TextField(
        "description", max_length=5000, blank=True, help_text="Video description."
    )

    @property
    def content_url(self):
        return YoutubeVideoURLConverter().to_url(self.item_id)

    def get_absolute_url(self):
        return reverse("youtubecontentitem_detail", kwargs={"item_id": self.item_id})

    @property
    def site_url(self):
        return "https://www.youtube.com/"

    @classmethod
    def site_name(self):
        return "YouTube"

    class Meta:
        verbose_name = "youtube video"


class AudioContentItem(ContentItem):
    duration = models.DurationField(
        help_text="Duration of episode.", blank=True, null=True
    )
    listen_count = models.PositiveIntegerField(
        help_text="Number of episode listens.", blank=True, null=True
    )

    class Meta:
        verbose_name = "episode"


class SpotifyContentItemQuerySet(ContentItemQuerySet):
    assemble_by_ids = assemble_spotify_content_items
    url_converters = ((SpotifyEpisodeURLConverter(), "item_id"),)


class SpotifyContentItem(AudioContentItem):
    objects = SpotifyContentItemQuerySet.as_manager()
    item_id = models.CharField(
        "episode ID", max_length=30, unique=True, help_text="Episode ID."
    )
    sp_show_id = models.CharField("show ID", max_length=30, help_text="Show ID.")
    sp_show_title = models.CharField(
        "show title", max_length=200, help_text="Show title."
    )
    sp_description = models.TextField(
        "description", max_length=5000, blank=True, help_text="Episode description."
    )

    @property
    def content_url(self):
        return SpotifyEpisodeURLConverter().to_url(self.item_id)

    def get_absolute_url(self):
        return reverse("spotifycontentitem_detail", kwargs={"item_id": self.item_id})

    @property
    def site_url(self):
        return "https://open.spotify.com/"

    @classmethod
    def site_name(self):
        return "Spotify"

    class Meta:
        verbose_name = "spotify episode"


class TextContentItem(ContentItem):
    word_count = models.PositiveIntegerField(
        blank=True, null=True, help_text="Word count."
    )
    text_html = models.TextField(
        "content text HTML", blank=True, help_text="Content text HTML."
    )
    text_plain = models.TextField(
        "content plaintext", blank=True, help_text="Content plaintext."
    )


class OBContentItemQuerySet(ContentItemQuerySet):
    assemble_by_ids = assemble_ob_content_items
    url_converters = (
        (OBPostLongURLConverter(), "item_id"),
        (OBPostShortURLConverter(), "ob_post_number"),
    )

    def download_new_items(self, min_edit_date=None):
        """Add posts whose names are not found in the database.

        Do not return items which were not successfully created.
        """
        self.update_last_edit_dates()
        if min_edit_date is None:
            try:
                # Take most recent edit date, among posts which haven't been edited
                # since creation
                min_edit_date = (
                    self.filter(edit_date__lt=F("create_timestamp"))
                    .latest("edit_date")
                    .edit_date
                )
            except self.model.DoesNotExist:
                # No items
                pass

        # sorting names by date is useful because: if there is an error during one batch
        # of downloads, calling this function again (after fixing the error) starts
        # downloading from the batch where the error occurred (rather than back at the
        # beginning)
        sorted_edit_dates = dict(
            sorted(assemble_ob_edit_dates().items(), key=lambda item: item[1])
        )
        sorted_site_names = [
            name
            for name, date in sorted_edit_dates.items()
            if min_edit_date is None or date > min_edit_date
        ]
        db_names = self.values_list("item_id", flat=True)
        sorted_missing_names = [
            name for name in sorted_site_names if name not in db_names
        ]

        created_item_count = self.bulk_create_items(sorted_missing_names)
        return created_item_count

    def update_edited_items(self):
        """Update posts with unsaved edits."""
        self.update_last_edit_dates()
        items_for_update = self.filter(edit_date__gte=F("download_timestamp"))
        updated_items = items_for_update.update_items()
        return [result[0] for result in updated_items]

    def update_last_edit_dates(self):
        """Synchronise edit dates with the overcomingbias site.

        This uses the bulk_update method, so does not change the update_timestamp field.
        """
        edit_dates = assemble_ob_edit_dates()

        all_items = self.all()
        for item in all_items:
            item.edit_date = edit_dates[item.item_id]
        update_count = self.bulk_update(all_items, ["edit_date"], batch_size=1000)

        return update_count


class OBContentItem(TextContentItem):
    objects = OBContentItemQuerySet.as_manager()
    item_id = models.CharField(
        "string ID",
        max_length=300,
        unique=True,
        help_text='Post string identifier. E.g. "2006/11/introduction"',
    )
    ob_post_number = models.PositiveIntegerField(
        "number ID", unique=True, help_text="Post number identifier."
    )
    disqus_id = models.CharField(
        max_length=400, blank=True, help_text="Post Disqus API string identifier."
    )
    ob_likes = models.PositiveSmallIntegerField(
        "likes", blank=True, null=True, help_text="Number of likes."
    )
    ob_comments = models.PositiveSmallIntegerField(
        "comments", blank=True, null=True, help_text="Number of comments."
    )

    @property
    def content_url(self):
        return OBPostLongURLConverter().to_url(self.item_id)

    def get_absolute_url(self):
        return reverse("obcontentitem_detail", kwargs={"item_id": self.item_id})

    @property
    def site_url(self):
        return "https://www.overcomingbias.com/"

    @classmethod
    def site_name(self):
        return "OvercomingBias"

    class Meta:
        verbose_name = "overcomingbias post"


class EssayContentItemQuerySet(ContentItemQuerySet):
    assemble_by_ids = assemble_essay_content_items
    url_converters = ((EssayURLConverter(), "item_id"),)


class EssayContentItem(TextContentItem):
    objects = EssayContentItemQuerySet.as_manager()
    item_id = models.CharField(
        "string ID",
        max_length=300,
        unique=True,
        help_text='Essay string identifier. E.g. "Varytax"',
    )

    @property
    def content_url(self):
        return EssayURLConverter().to_url(self.item_id)

    def get_absolute_url(self):
        return reverse("essaycontentitem_detail", kwargs={"item_id": self.item_id})

    @property
    def site_url(self):
        return "https://mason.gmu.edu/~rhanson/"

    @classmethod
    def site_name(self):
        return "Home Page"

    class Meta:
        verbose_name = "essay"
