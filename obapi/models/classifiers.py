from django.db import models, transaction
from django.urls import reverse
from obapi import utils
from obapi.modelfields import SimpleSlugField


class AliasedModel(models.Model):
    """Base class for models with aliases."""

    name = models.CharField(max_length=100, unique=True, help_text="Name.")
    description = models.CharField(
        max_length=100, help_text="Brief description.", blank=True
    )

    class Meta:
        abstract = True

    def get_slug(self):
        return self.aliases.get(protected=True).text

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save an AliasedModel instance.

        Raises
        ------
        IntegrityError
            If the instance `name` is already an alias of another instance.
        """
        with transaction.atomic():
            # (1) Save model instance
            super().save(*args, **kwargs)
            # (2) Set and protect `name` alias
            self.aliases.all().update(protected=False)
            self.aliases.update_or_create(
                text=utils.slugify(self.name),
                defaults={"protected": True},
            )

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

    text = SimpleSlugField(
        max_length=utils.SLUG_MAX_LENGTH, help_text="Alias text.", unique=True
    )
    protected = models.BooleanField(
        default=False,
        editable=False,
        help_text="True for the alias which equals the owner name.",
    )
    owner = None

    class Meta:
        abstract = True
        verbose_name_plural = "aliases"

    def __str__(self):
        return self.text

    def clean(self):
        self.text = utils.slugify(self.text)
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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
