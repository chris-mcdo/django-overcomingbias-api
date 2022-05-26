from django.db import models
from obapi import utils
from obapi.modelfields import SimpleSlugField
from ordered_model.models import OrderedModel

SEQUENCE_SLUG_MAX_LENGTH = 150


class BaseSequence(models.Model):
    """Base class for Sequence models."""

    title = models.CharField(max_length=100, help_text="Sequence title.")
    slug = SimpleSlugField(max_length=SEQUENCE_SLUG_MAX_LENGTH, editable=False)
    abstract = models.TextField(
        blank=True, max_length=5000, help_text="Description of sequence."
    )
    items = models.ManyToManyField("ContentItem", through="BaseSequenceMember")

    def __str__(self):
        return self.title

    class Meta:
        abstract = True

    def clean(self):
        # Set slug from title
        self.slug = utils.to_slug(self.title, max_length=SEQUENCE_SLUG_MAX_LENGTH)
        super().clean()

    def save(self, *args, **kwargs):
        """Save a Sequence object."""
        self.clean()
        super().save(*args, **kwargs)


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_sequence_slug")
        ]


class SequenceMember(BaseSequenceMember):
    sequence = models.ForeignKey(
        Sequence,
        on_delete=models.CASCADE,
        related_name="members",
        related_query_name="members",
    )
