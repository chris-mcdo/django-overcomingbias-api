from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from obapi import utils


class AliasedModel(models.Model):
    """Base class for models with aliases."""

    name = models.CharField(max_length=100, unique=True, help_text="Name.")
    slug = models.SlugField(max_length=100, unique=True, null=True, editable=False)
    description = models.CharField(
        max_length=100, help_text="Brief description.", blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save an AliasedModel instance.

        Raises
        ------
        IntegrityError
            If the instance `name` is already an alias of another instance.
        """
        try:
            with transaction.atomic():
                # (1) Update slug
                self.slug = utils.to_slug(self.name)
                # (2) Save model instance
                super().save(*args, **kwargs)
                # (3) un-protect all aliases
                self.aliases.all().update(protected=False)
                # (4) create and protect <instance name> alias
                self.aliases.update_or_create(
                    text__iexact=self.name,
                    defaults={"text": self.name, "protected": True},
                )
                # (5) create and protect <slug> alias (if needed)
                self.aliases.update_or_create(
                    text__iexact=self.slug,
                    defaults={"text": self.slug, "protected": True},
                )
        except IntegrityError as e:
            raise IntegrityError(
                f"The name {self.name}"
                f" is an alias of another {self._meta.verbose_name}."
            ) from e

    def get_absolute_url(self):
        model_name = self._meta.verbose_name
        return reverse(
            "explore_detail",
            kwargs={"model_name": model_name, "instance_name": self.slug},
        )


class Author(AliasedModel):
    description = None


class Idea(AliasedModel):
    pass


class Topic(AliasedModel):
    pass


class Tag(AliasedModel):
    description = None


class Alias(models.Model):
    """Base class for models which represent aliases of other models.

    `owner` is the Foreign Key to the aliased model. The aliased model should have a
    `name` attribute, or the subclass should override the __str__ method.
    """

    text = models.CharField(max_length=100, help_text="Alias text.")
    protected = models.BooleanField(
        default=False,
        editable=False,
        help_text="True for the alias which equals the owner name.",
    )
    owner = None

    class Meta:
        abstract = True
        verbose_name_plural = "aliases"
        constraints = [UniqueConstraint(Lower("text"), name="%(class)s_is_unique")]

    def __str__(self):
        return f"{self.text} ({self.owner.name})"

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if exclude is not None and "text" in exclude:
            return
        # Raise error if there is a matching alias, and the match has a different pk
        try:
            match = type(self).objects.get(text__iexact=self.text)
        except type(self).DoesNotExist:
            return
        else:
            if match != self:
                self.owner.refresh_from_db(fields=["name"])
                raise ValidationError(
                    {"text": "This alias is already taken."}, code="invalid"
                )


class AuthorAlias(Alias):
    owner = models.ForeignKey(
        Author,
        verbose_name="author",
        on_delete=models.CASCADE,
        related_name="aliases",
        related_query_name="alias",
        help_text="Author the alias refers to.",
    )


class IdeaAlias(Alias):
    owner = models.ForeignKey(
        Idea,
        verbose_name="idea",
        on_delete=models.CASCADE,
        related_name="aliases",
        related_query_name="alias",
        help_text="Idea the alias refers to.",
    )


class TopicAlias(Alias):
    owner = models.ForeignKey(
        Topic,
        verbose_name="topic",
        on_delete=models.CASCADE,
        related_name="aliases",
        related_query_name="alias",
        help_text="Topic the alias refers to.",
    )


class TagAlias(Alias):
    owner = models.ForeignKey(
        Tag,
        verbose_name="tag",
        on_delete=models.CASCADE,
        related_name="aliases",
        related_query_name="alias",
        help_text="Tag the alias refers to.",
    )


class ExternalLink(models.Model):
    """Model representing link to "external" content.

    Here "external" means "outside the database".
    """

    url = models.URLField(unique=True, help_text="Link URL.")

    def __str__(self):
        return self.url
