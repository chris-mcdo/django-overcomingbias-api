from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from obapi import utils
from obapi.modelfields import SimpleSlugField
from ordered_model.models import OrderedModel


class BaseSequence(models.Model):
    """Base class for Sequence models."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name="%(class)ss",
    )
    title = models.CharField(max_length=100, help_text="Sequence title.")
    slug = SimpleSlugField(max_length=utils.SLUG_MAX_LENGTH, editable=False)
    description = models.TextField(
        blank=True, max_length=5000, help_text="Description of sequence."
    )
    items = models.ManyToManyField("ContentItem", through="BaseSequenceMember")
    public = models.BooleanField(
        default=False, help_text="Whether the sequence is public or private."
    )

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "slug"], name="unique_%(class)s_slug"
            )
        ]

    def clean(self):
        # Set slug from title
        self.slug = utils.to_slug(self.title)
        super().clean()

    def save(self, *args, **kwargs):
        """Save a Sequence object."""
        self.clean()
        super().save(*args, **kwargs)

    def export(self, output_format="md", output_file=None):
        import pypandoc

        if output_file is None:
            output_file = f"output/sequence-{self.pk}.{output_format}"

        metadata_template = f"{self._meta.app_label}/export/metadata.md"
        metadata = render_to_string(metadata_template, {"sequence": self})

        items = self.items.select_subclasses()
        markdown_items = [item.export(output_format="md") for item in items]

        markdown_full_text = "\n".join([metadata] + markdown_items)

        pypandoc.convert_text(
            markdown_full_text, to=output_format, format="md", outputfile=output_file
        )


class BaseSequenceMember(OrderedModel):
    """Base class for Sequence items."""

    order_with_respect_to = "sequence"
    content_item = models.ForeignKey(
        "ContentItem",
        on_delete=models.CASCADE,
        related_name="sequence_members",
        related_query_name="sequence_members",
    )
    sequence = models.ForeignKey(
        BaseSequence,
        on_delete=models.CASCADE,
        related_name="members",
        related_query_name="members",
    )

    class Meta:
        ordering = ("sequence", "order")
        abstract = True

    def __str__(self):
        return f"{self.content_item.title} ({self.sequence.title})"


class Sequence(BaseSequence):
    items = models.ManyToManyField("ContentItem", through="SequenceMember")


class SequenceMember(BaseSequenceMember):
    sequence = models.ForeignKey(
        Sequence,
        on_delete=models.CASCADE,
        related_name="members",
        related_query_name="members",
    )
