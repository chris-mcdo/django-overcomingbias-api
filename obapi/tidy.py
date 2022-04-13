import datetime
import re

from dateutil.parser import isoparse

from obapi import utils


def tidy_youtube_videos_json(video_ids, raw_json):
    items = raw_json["items"]

    # Set item to None if not present
    video_dict = {item["id"]: item for item in items}
    for video_id in video_ids:
        video_dict.setdefault(video_id, None)
    videos = [video_dict[video_id] for video_id in video_ids]

    return [_tidy_youtube_video_json(video) for video in videos]


def tidy_spotify_episodes_json(episode_ids, raw_json):
    items = raw_json["episodes"]

    # Set item to None if not present
    episode_dict = {item["id"]: item for item in items}
    for episode_id in episode_ids:
        episode_dict.setdefault(episode_id, None)
    episodes = [episode_dict[episode_id] for episode_id in episode_ids]

    return [_tidy_spotify_episode_json(episode) for episode in episodes]


def tidy_ob_post_objects(post_names, post_dict):
    posts = [post_dict[post_name] for post_name in post_names]
    return [_tidy_ob_post_object(post) for post in posts]


def _tidy_youtube_video_json(item_json):
    """Tidy a YouTube API v3 response into a dictionary."""
    if item_json is None:
        return None
    video = {
        "author_names": [item_json["snippet"]["channelTitle"]],
        "classifier_names": item_json["snippet"].get("tags", []),
        "title": item_json["snippet"]["title"],
        "description_html": utils.plaintext_to_html(
            item_json["snippet"].get("description", "")
        ),
        "publish_date": isoparse(item_json["snippet"]["publishedAt"]),
        "duration": utils.parse_duration(item_json["contentDetails"]["duration"]),
        "view_count": int(item_json["statistics"]["viewCount"]),
        "item_id": item_json["id"],
        "yt_channel_id": item_json["snippet"]["channelId"],
        "yt_channel_title": item_json["snippet"]["channelTitle"],
        "yt_likes": item_json["statistics"].get("likeCount", None),
        "yt_description": item_json["snippet"].get("description", ""),
    }
    return video


def _tidy_spotify_episode_json(item_json):
    if item_json is None:
        return None
    episode = {
        "author_names": [item_json["show"]["publisher"]],
        "title": item_json["name"],
        "description_html": item_json["html_description"],
        "publish_date": isoparse(item_json["release_date"]).replace(
            tzinfo=datetime.timezone.utc
        ),
        "duration": datetime.timedelta(milliseconds=item_json["duration_ms"]),
        "item_id": item_json["id"],
        "sp_show_id": item_json["show"]["id"],
        "sp_show_title": item_json["show"]["name"],
        "sp_description": item_json["description"],
    }
    return episode


def _tidy_ob_post_object(item_post):
    if item_post is None:
        return None
    internal_links = [_tidy_ob_internal_link(link) for link in item_post.internal_links]
    post = {
        "author_names": [item_post.author],
        "classifier_names": [*item_post.tags, *item_post.categories],
        "link_urls": [*internal_links, *item_post.external_links],
        "title": item_post.title,
        "publish_date": item_post.publish_date,
        "edit_date": item_post.edit_date,
        "word_count": item_post.word_count,
        "text_html": item_post.text_html,
        "text_plain": item_post.plaintext,
        "item_id": item_post.name,
        "ob_post_number": item_post.number,
        "disqus_id": item_post.disqus_id,
        "ob_likes": item_post.votes,
        "ob_comments": item_post.comments,
    }
    return post


def _tidy_ob_internal_link(url: str):
    """Fix common errors with internal links."""
    url = url.strip()  # strip whitespace
    url = re.sub(r"\.htm(?!l)", ".html", url)  # ensure .html not .htm
    url = re.sub(r"-+", "-", url)  # collapse duplicate hyphens
    url = re.sub(r"-\.html", ".htm", url)  # remove trailing hyphens
    return url
