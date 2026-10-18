from datetime import datetime
from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.urls import register_converter
from ninja import ModelSchema, NinjaAPI, Query
from pydantic import conint, constr

from obapi.converters import (
    ESSAY_ID_REGEX,
    OB_POST_NAME_REGEX,
    SPOTIFY_EPISODE_ID_REGEX,
    YOUTUBE_VIDEO_ID_REGEX,
    ClassifierNameConverter,
    EssayIDConverter,
    OBPostNameConverter,
    SpotifyEpisodeIDConverter,
    YoutubeVideoIDConverter,
)
from obapi.models import (
    ContentItem,
    EssayContentItem,
    OBContentItem,
    SpotifyContentItem,
    YoutubeContentItem,
)

# Custom URL converters
register_converter(YoutubeVideoIDConverter, "youtube_id")
register_converter(SpotifyEpisodeIDConverter, "spotify_id")
register_converter(OBPostNameConverter, "ob_name")
register_converter(EssayIDConverter, "essay_id")
register_converter(ClassifierNameConverter, "classifier")

# API
api = NinjaAPI(
    title="OB API", description="API for Robin Hanson's content", urls_namespace="api"
)

CONTENT_TYPES = (
    f"{prefix}contentitem" for prefix in ("ob", "essay", "spotify", "youtube")
)


# API exception handlers
@api.exception_handler(ObjectDoesNotExist)
def object_not_found(request, exc):
    return api.create_response(
        request,
        {"message": str(exc)},
        status=404,
    )


# Schemas
class ContentItemSchema(ModelSchema):
    authors: List[str]
    ideas: List[str]
    topics: List[str]
    tags: List[str]
    item_id: str
    url: str

    @staticmethod
    def resolve_url(obj):
        return obj.content_url

    @staticmethod
    def resolve_authors(obj):
        return [author.name for author in obj.authors.all()]

    @staticmethod
    def resolve_ideas(obj):
        return [idea.name for idea in obj.ideas.all()]

    @staticmethod
    def resolve_topics(obj):
        return [topic.name for topic in obj.topics.all()]

    @staticmethod
    def resolve_tags(obj):
        return [tag.name for tag in obj.tags.all()]

    @staticmethod
    def resolve_item_id(obj):
        return obj.item_id

    class Meta:
        model = ContentItem
        fields = ["title", "publish_date", "edit_date"]


class OBContentItemSchema(ContentItemSchema, ModelSchema):
    class Meta:
        model = OBContentItem
        fields = [
            "item_id",
            "title",
            "publish_date",
            "edit_date",
            "ob_post_number",
            "disqus_id",
            "ob_likes",
            "ob_comments",
            "word_count",
            "text_html",
        ]


class EssayContentItemSchema(ContentItemSchema, ModelSchema):
    class Meta:
        model = EssayContentItem
        fields = [
            "item_id",
            "title",
            "publish_date",
            "edit_date",
            "word_count",
            "text_html",
        ]


class YoutubeContentItemSchema(ContentItemSchema, ModelSchema):
    class Meta:
        model = YoutubeContentItem
        fields = [
            "item_id",
            "title",
            "publish_date",
            "edit_date",
            "yt_channel_id",
            "yt_channel_title",
            "yt_likes",
            "duration",
            "view_count",
        ]


class SpotifyContentItemSchema(ContentItemSchema, ModelSchema):
    class Meta:
        model = SpotifyContentItem
        fields = [
            "item_id",
            "title",
            "publish_date",
            "edit_date",
            "sp_show_id",
            "sp_show_title",
            "duration",
            "listen_count",
        ]


# Helper functions
def _list_all_content():
    """Efficiently query database for content items."""
    id_fields = (f"{content_type}__item_id" for content_type in CONTENT_TYPES)
    return (
        ContentItem.objects.only(
            *ContentItemSchema.Meta.fields,
            *id_fields,
        )
        .select_subclasses()
        .prefetch_related("authors", "ideas", "topics", "tags")
    )


# API operations
@api.get(
    "/content/list/all",
    response=List[ContentItemSchema],
    summary="List All Content",
    description="List basic information about all content items",
    tags=["content"],
)
def list_all_content(request):
    return _list_all_content()


@api.get(
    "/content/list/date",
    response=List[ContentItemSchema],
    summary="List Content By Publication Date",
    tags=["content"],
)
def list_content_by_date(
    request, before: Optional[datetime], after: Optional[datetime]
):
    items = _list_all_content()
    if after:
        items = items.filter(publish_date__gte=after)
    if before:
        items = items.filter(publish_date__lte=before)
    return items


@api.get(
    "/content/list/recent",
    response=List[ContentItemSchema],
    summary="List Most Recent Content",
    tags=["content"],
)
def list_recent_content(request, offset: conint(ge=0) = 0, count: conint(gt=0) = 10):
    return _list_all_content().order_by("-publish_date")[offset : offset + count]


@api.get(
    "content/overcomingbias",
    response=List[OBContentItemSchema],
    summary="Get OvercomingBias Posts",
    tags=["content"],
)
def get_overcomingbias_posts(
    request, ids: List[constr(pattern=OB_POST_NAME_REGEX)] = Query(...)
):
    return (
        OBContentItem.objects.only(*OBContentItemSchema.Meta.fields)
        .prefetch_related("authors", "ideas", "topics", "tags")
        .filter(item_id__in=ids)
    )


@api.get(
    "content/essays",
    response=List[EssayContentItemSchema],
    summary="Get Essays",
    tags=["content"],
)
def get_essays(request, ids: List[constr(pattern=ESSAY_ID_REGEX)] = Query(...)):
    return (
        EssayContentItem.objects.only(*EssayContentItemSchema.Meta.fields)
        .prefetch_related("authors", "ideas", "topics", "tags")
        .filter(item_id__in=ids)
    )


@api.get(
    "content/youtube",
    response=List[YoutubeContentItemSchema],
    summary="Get YouTube Videos",
    tags=["content"],
)
def get_youtube_videos(
    request, ids: List[constr(pattern=YOUTUBE_VIDEO_ID_REGEX)] = Query(...)
):
    return (
        YoutubeContentItem.objects.only(*YoutubeContentItemSchema.Meta.fields)
        .prefetch_related("authors", "ideas", "topics", "tags")
        .filter(item_id__in=ids)
    )


@api.get(
    "content/spotify",
    response=List[SpotifyContentItemSchema],
    summary="Get Spotify Episodes",
    tags=["content"],
)
def get_spotify_episodes(
    request, ids: List[constr(pattern=SPOTIFY_EPISODE_ID_REGEX)] = Query(...)
):
    return (
        SpotifyContentItem.objects.only(*SpotifyContentItemSchema.Meta.fields)
        .prefetch_related("authors", "ideas", "topics", "tags")
        .filter(item_id__in=ids)
    )
