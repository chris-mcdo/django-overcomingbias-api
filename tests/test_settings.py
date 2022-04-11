# Applications

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "obapi",
]

# Secrets
SECRET_KEY = "fake-key"

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
