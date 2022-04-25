import re

from django.core.validators import RegexValidator

validate_simple_slug = RegexValidator(
    re.compile(r"^[-a-z0-9]+\Z"),
    "Enter a valid “slug” consisting of lowercase letters, numbers or hyphens.",
    "invalid",
)
