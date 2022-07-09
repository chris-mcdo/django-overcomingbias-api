"""Download raw API data from the web."""

from base64 import b64encode

import cachetools.func
import httpx
from django.conf import settings
from obscraper import get_edit_dates, get_posts_by_names

from obapi import exceptions


def download_youtube_videos_json(video_ids):
    api_url = "https://youtube.googleapis.com/youtube/v3/videos"
    payload = {
        "id": ",".join(video_ids),
        "part": ("snippet", "contentDetails", "statistics"),
        "key": settings.YOUTUBE_API_KEY,
    }
    response = httpx.get(url=api_url, params=payload)
    _raise_for_status(response)
    return response.json()


def download_spotify_episodes_json(episode_ids):
    api_url = "https://api.spotify.com/v1/episodes/"
    headers = {"Authorization": f"Bearer {_get_spotify_api_token()}"}
    params = {"ids": ",".join(episode_ids), "market": "US"}
    response = httpx.get(url=api_url, headers=headers, params=params)
    _raise_for_status(response)
    return response.json()


def download_ob_post_objects(post_names):
    try:
        post_dict = get_posts_by_names(post_names)
    except ValueError as err:
        raise exceptions.APICallError("API call failed.") from err
    else:
        return post_dict


def download_ob_edit_dates():
    return get_edit_dates()


def download_essays(essay_ids):
    base_url = "https://mason.gmu.edu/~rhanson/"
    default_headers = {"user-agent": "Mozilla/5.0"}
    essay_dict = {}
    with httpx.Client(headers=default_headers) as client:
        for essay_id in essay_ids:
            essay_url = f"{base_url}/{essay_id}.html"
            response = client.get(essay_url)
            _raise_for_status(response)
            essay_dict[essay_id] = response.text
    return essay_dict


@cachetools.func.ttl_cache(ttl=3)
def _get_spotify_api_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode("ascii")
    ).decode("ascii")
    headers = {"Authorization": f"Basic {auth_header}"}
    payload = {"grant_type": "client_credentials"}
    response = httpx.post(url=auth_url, data=payload, headers=headers)
    _raise_for_status(response)
    token_info = response.json()
    return token_info["access_token"]


def _raise_for_status(response):
    try:
        response.raise_for_status()
    except httpx.HTTPError as err:
        raise exceptions.APICallError("API call failed.") from err
