from django import forms

import obapi.export
import obapi.validators


class SimpleSlugField(forms.CharField):
    default_validators = [obapi.validators.validate_simple_slug]


class PandocWriterField(forms.ChoiceField):
    """A form field for selecting a Sequence export format."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writers = {
            Writer.pandoc_name: Writer
            for Writer in obapi.export.get_supported_writers()
        }

        self.choices = [
            (writer_name, writer_name) for writer_name in self.writers.keys()
        ]

    def clean(self, value):
        value = super().clean(value)
        try:
            return self.writers[value]
        except KeyError:
            raise forms.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
