from django.db import models

import obapi.formfields
from obapi import validators


class SimpleSlugField(models.CharField):
    default_validators = [validators.validate_simple_slug]
    description = "Custom slug (up to %(max_length)s)"

    def __init__(self, *args, max_length=50, db_index=True, **kwargs):
        super().__init__(*args, max_length=max_length, db_index=db_index, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == 50:
            del kwargs["max_length"]
        if self.db_index is False:
            kwargs["db_index"] = False
        else:
            del kwargs["db_index"]
        return name, path, args, kwargs

    def get_internal_type(self):
        return "SlugField"

    def formfield(self, **kwargs):
        return super().formfield(
            **{"form_class": obapi.formfields.SimpleSlugField, **kwargs}
        )
