import os

# Applications

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "obapi",
]

# Secrets
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fake-key")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


# Debug mode
DEBUG = False

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/


USE_TZ = True

TIME_ZONE = "UTC"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
