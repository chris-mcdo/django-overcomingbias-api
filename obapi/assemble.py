"""Download and tidy API data.

These functions return ContentItem data in a standard format understood by the
ContentItemManager.
"""
import datetime
from functools import wraps

from obapi.download import (
    download_essays,
    download_ob_edit_dates,
    download_ob_post_objects,
    download_spotify_episodes_json,
    download_youtube_videos_json,
)
from obapi.tidy import (
    tidy_essays,
    tidy_ob_post_objects,
    tidy_spotify_episodes_json,
    tidy_youtube_videos_json,
)


def download_timestamp(decorated_function):
    """Attach a timestamp to result of a function.

    Attaches a `download_timestamp` attribute to the result of the function, which
    specifies the time when the function was called.

    If the output of the function is not a list of dictionaries (e.g. if it is None),
    it does nothing.
    """

    @wraps(decorated_function)
    def decorator(*args, **kwargs):
        download_timestamp = datetime.datetime.now(datetime.timezone.utc)
        result = decorated_function(*args, **kwargs)
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    item["download_timestamp"] = download_timestamp
        return result

    return decorator


@download_timestamp
def assemble_youtube_content_items(video_ids):
    raw_json = download_youtube_videos_json(video_ids)
    tidy_dict = tidy_youtube_videos_json(video_ids, raw_json)
    return tidy_dict


@download_timestamp
def assemble_spotify_content_items(episode_ids):
    raw_json = download_spotify_episodes_json(episode_ids)
    tidy_dict = tidy_spotify_episodes_json(episode_ids, raw_json)
    return tidy_dict


@download_timestamp
def assemble_ob_content_items(post_names):
    post_dict = download_ob_post_objects(post_names)
    tidy_dict = tidy_ob_post_objects(post_names, post_dict)
    return tidy_dict


@download_timestamp
def assemble_essay_content_items(essay_ids):
    essay_dict = download_essays(essay_ids)
    tidy_dict = tidy_essays(essay_ids, essay_dict)
    return tidy_dict


def assemble_ob_edit_dates():
    return download_ob_edit_dates()
