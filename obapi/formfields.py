from django import forms

from obapi import validators


class SimpleSlugField(forms.CharField):
    default_validators = [validators.validate_simple_slug]
