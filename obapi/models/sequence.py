from django.conf import settings
from django.db import models
from ordered_model.models import OrderedModel


class Sequence(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, help_text="Sequence title.")
    description = models.TextField(
        blank=True, max_length=5000, help_text="Description of sequence."
    )
    items = models.ManyToManyField("ContentItem", through="SequenceMember")
    public = models.BooleanField(
        default=False, help_text="Whether the sequence is public or private."
    )

    def __str__(self):
        return self.title


class SequenceMember(OrderedModel):
    content_item = models.ForeignKey(
        "ContentItem",
        on_delete=models.CASCADE,
        related_name="sequence_members",
        related_query_name="sequence_members",
    )
    sequence = models.ForeignKey(
        Sequence,
        on_delete=models.CASCADE,
        related_name="members",
        related_query_name="members",
    )
    order_with_respect_to = "sequence"

    class Meta:
        ordering = ("sequence", "order")

    def __str__(self):
        return f"{self.content_item.title} ({self.sequence.title})"
