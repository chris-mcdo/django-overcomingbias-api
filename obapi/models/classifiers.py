from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from obapi import utils
from obapi.modelfields import SimpleSlugField

CLASSIFIER_SLUG_MAX_LENGTH = 150


class AliasedModelQuerySet(models.QuerySet):
    def create_with_aliases(self, aliases=None, **kwargs):
        """Save an object with some aliases.

        Assumes that the given aliases have been cleaned.
        """
        aliases = set(aliases)
        with transaction.atomic():
            new_object = self.create(**kwargs)
            aliases.discard(new_object.slug)
            for alias in aliases:
                new_object.aliases.create(text=alias)
        return new_object

    def merge_objects(self):
        """Merge a QuerySet of objects."""
        new_fields = {}

        # Make list of aliases
        alias_model = self.model.aliases.field.model
        aliases_queryset = alias_model.objects.filter(owner__in=self)
        aliases = set(aliases_queryset.values_list("text", flat=True))

        # Use name of first object in QuerySet
        new_fields["name"] = self.first().name

        # Create new description (if description field exists)
        try:
            max_length = self.model.description.field.max_length
        except AttributeError:
            pass
        else:
            description_list = self.values_list("description", flat=True)
            description = "/".join([desc for desc in description_list if desc != ""])
            new_fields["description"] = description[0:max_length]

        with transaction.atomic():
            # Collect related content
            contentitem_field = self.model.content.field
            items = list(
                contentitem_field.model.objects.filter(
                    **{f"{contentitem_field.name}__in": self}
                ).distinct()
            )

            # Delete old object, create new
            self.delete()
            new_object = self.create_with_aliases(aliases=aliases, **new_fields)

            # Add related content
            new_object.content.add(*items)

        return new_object


class AliasedModel(models.Model):
    """Base class for models with aliases."""

    objects = AliasedModelQuerySet().as_manager()

    name = models.CharField(max_length=100, unique=True, help_text="Name.")
    slug = SimpleSlugField(
        max_length=CLASSIFIER_SLUG_MAX_LENGTH, unique=True, editable=False
    )
    description = models.CharField(
        max_length=100, help_text="Brief description.", blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        # Set slug from title
        self.slug = utils.to_slug(self.name, max_length=CLASSIFIER_SLUG_MAX_LENGTH)
        super().clean()

    def save(self, *args, **kwargs):
        """Save an AliasedModel instance.

        Raises
        ------
        IntegrityError
            If the instance `name` is already an alias of another instance.
        """
        # (1) Clean and set slug
        self.clean()
        with transaction.atomic():
            # (2) Save model instance
            super().save(*args, **kwargs)
            # (3) Set and protect `slug` alias
            self.aliases.all().update(protected=False)
            self.aliases.update_or_create(
                text=self.slug,
                defaults={"protected": True},
            )

    def get_absolute_url(self):
        model_name = self._meta.verbose_name
        return reverse(
            "explore_detail",
            kwargs={"model_name": model_name, "instance_name": self.slug},
        )

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if exclude is not None and "text" in exclude:
            return
        # Raise error if there is a matching alias, and the match has a different pk
        alias_model = self.aliases.model
        try:
            match = alias_model.objects.get(
                text=utils.to_slug(self.name, max_length=CLASSIFIER_SLUG_MAX_LENGTH)
            )
        except alias_model.DoesNotExist:
            return
        else:
            if match.owner != self:
                self.refresh_from_db(fields=["name"])
                raise ValidationError(
                    {"name": "The alias of this name is already taken."}, code="invalid"
                )

    def convert_object(self, model):
        """Convert object to another type."""
        with transaction.atomic():
            # Initialise fields
            new_fields = {
                "name": self.name,
                "aliases": self.aliases.values_list("text", flat=True),
            }
            if model.description:
                if (old_description := self.description) is None:
                    new_fields["description"] = ""
                else:
                    new_fields["description"] = old_description

            # Create new object
            new_object = model.objects.create_with_aliases(**new_fields)

            # Update related content
            items = self.content.all()
            new_object.content.add(*items)

            # Delete old object
            self.delete()

        return new_object


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
        max_length=CLASSIFIER_SLUG_MAX_LENGTH, help_text="Alias text.", unique=True
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
        self.text = utils.to_slug(self.text, max_length=CLASSIFIER_SLUG_MAX_LENGTH)
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

    url = models.URLField(max_length=2048, help_text="Link URL.")

    def __str__(self):
        return self.url
