import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from obapi import utils
from obapi.models import Author, ContentItem, Idea, Tag, Topic
from obapi.models.classifiers import CLASSIFIER_SLUG_MAX_LENGTH, IdeaAlias, TopicAlias


@pytest.mark.django_db
class TestCreateAliasedModel:
    def test_create_valid_topic(self):
        # Act
        Topic.objects.create(name="Law&Øther", description="Law and other topics.")

        # Assert
        obj = Topic.objects.get(name="Law&Øther")
        assert obj.name == "Law&Øther"
        assert obj.slug == "law-other"
        assert obj.description == "Law and other topics."

        obj_aliases = obj.aliases.all()
        assert obj_aliases.count() == 1

        alias = obj_aliases.get()
        assert alias.text == "law-other"
        assert alias.protected

    def test_create_valid_topic_with_aliases(self):
        # Act
        topic = Topic.objects.create(name="topic-two")
        topic.aliases.create(text="Second Topic")

        # Assert
        obj = Topic.objects.get(name="topic-two")
        assert obj.name == "topic-two"
        assert obj.slug == obj.name
        assert obj.description == ""

        obj_aliases = obj.aliases.all()
        assert obj_aliases.count() == 2

        expected_aliases = {"topic-two", "second-topic"}
        actual_aliases = set(obj_aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases

        name_alias = obj_aliases.get(text="topic-two")
        assert name_alias.protected

    @pytest.mark.parametrize(
        "new_name,new_slug",
        [
            ("Law&Other", "law-other"),
            ("law other", "law-other"),
            ("law-other", "law-other"),
            ("LawOther", "lawother"),
        ],
    )
    def test_change_topic_name(self, new_name, new_slug):
        # Act
        example = Topic.objects.create(
            name="Law&Øther", description="Law and other topics."
        )
        example.name = new_name
        example.save()

        # Assert
        assert example.name == new_name
        assert example.slug == new_slug

    def test_can_create_another_object_type_with_same_name(self):
        # Act
        topic = Topic.objects.create(name="Duplicated", description="A duplicate.")
        idea = Idea.objects.create(name="Duplicated", description="A duplicate.")

        # Assert
        assert topic.name == idea.name
        assert topic.slug == idea.slug
        topic_alias_set = set(topic.aliases.values_list("text", flat=True))
        idea_alias_set = set(idea.aliases.values_list("text", flat=True))
        assert topic_alias_set == idea_alias_set

    def test_cannot_duplicate_aliases(self):
        # Arrange
        topic = Topic.objects.create(name="Law&Other", description="About law.")
        topic.aliases.create(text="law-etc")

        # Act & assert
        # Same name and description
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Law&Other", description="About law.")

        # Different name, same slug
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Law Other")

        # Name = existing alias
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="law-etc")

        # Slug = existing alias
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Law, Etc.")


@pytest.mark.django_db
class TestCreateWithAliases:
    @pytest.mark.parametrize(
        "topic_name,aliases,alias_count",
        [
            ("Law Other", [], 1),
            ("Law Other", ["law", "norms"], 3),
            ("Law Other", ["law-other"], 1),
        ],
    )
    def test_create_valid_topics(self, topic_name, aliases, alias_count):
        # Act
        t1 = Topic.objects.create_with_aliases(name=topic_name, aliases=aliases)

        # Assert
        assert t1.name == topic_name
        assert t1.slug == utils.to_slug(
            topic_name, max_length=CLASSIFIER_SLUG_MAX_LENGTH
        )
        assert t1.aliases.count() == alias_count

    @pytest.mark.parametrize(
        "topic_name,aliases", [("Law", ["legal"]), ("Legal", ["lawyer", "norms"])]
    )
    def test_fails_with_invalid_names(self, topic_name, aliases):
        # Arrange
        Topic.objects.create_with_aliases(name="Law", aliases=["law-etc", "norms"])

        # Act & Assert
        with pytest.raises(IntegrityError):
            Topic.objects.create_with_aliases(name=topic_name, aliases=aliases)


@pytest.mark.django_db
class TestValidateUniqueAlias:
    def test_succeeds_for_unique_aliases(self):
        # Arrange
        law = Topic.objects.create(name="Law", description="About law.")
        law.aliases.create(text="legal")
        norms = Topic.objects.create(name="Norms", description="About norms.")
        social = TopicAlias(text="social-norms", owner=norms)

        # Act & assert
        try:
            social.full_clean()  # not yet saved
        except ValidationError:
            pytest.fail("ValidationError raised with unique aliases.")
        social.save()
        try:
            social.full_clean()
        except ValidationError:
            pytest.fail("ValidationError raised with unique aliases.")

    def test_succeeds_when_another_object_type_has_same_alias(self):
        # Arrange
        law_topic = Topic.objects.create(name="Law", description="About law.")
        law_topic.aliases.create(text="rules")
        norms_idea = Idea.objects.create(name="Norms", description="About norms.")
        rules = IdeaAlias(text="rules", owner=norms_idea)

        # Act & assert
        try:
            rules.full_clean()  # not yet saved
        except ValidationError:
            pytest.fail("ValidationError raised with unique aliases.")
        rules.save()
        try:
            rules.full_clean()
        except ValidationError:
            pytest.fail("ValidationError raised with unique aliases.")

    @pytest.mark.parametrize("alias_text", ["Law", "law", "Rules", "rulEs"])
    def test_fails_with_duplicate_aliases(self, alias_text):
        # Arrange
        law = Topic.objects.create(name="Law", description="About law.")
        law.aliases.create(text="Rules")
        norms = Topic.objects.create(name="Norms", description="About norms.")

        # Act & Assert
        norms_alias = TopicAlias(text=alias_text, owner=norms)
        with pytest.raises(ValidationError):
            norms_alias.full_clean()


@pytest.mark.django_db
class TestMergeObjects:
    def test_preserves_related_content_for_topics(self):
        # Arrange - create topics and related content
        law = Topic.objects.create_with_aliases(name="Law", aliases=["legal", "laws"])
        norms = Topic.objects.create_with_aliases(name="Norms", aliases=["norm"])

        now = datetime.datetime.now()
        video = ContentItem.objects.create(title="Video Item", publish_date=now)
        audio = ContentItem.objects.create(title="Audio Item", publish_date=now)
        text = ContentItem.objects.create(title="Text Item", publish_date=now)

        law.content.add(video, audio)
        norms.content.add(text)

        # Act
        merged_object = Topic.objects.all().merge_objects()

        # Assert
        assert not Topic.objects.filter(pk__in=[law.pk, norms.pk])

        expected_content = {video, audio, text}
        assert set(merged_object.content.all()) == expected_content

        expected_names = ("Law", "Norms")
        assert merged_object.name in expected_names

        expected_aliases = {"law", "legal", "laws", "norms", "norm"}
        actual_aliases = set(merged_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases

    def test_can_merge_objects_without_descriptions(self):
        # Arrange
        law = Tag.objects.create_with_aliases(name="Law", aliases=["legal", "laws"])
        norms = Tag.objects.create_with_aliases(name="Norms", aliases=["norm"])

        # Act
        merged_object = Tag.objects.all().merge_objects()

        # Assert
        assert not Tag.objects.filter(pk__in=[law.pk, norms.pk])

        expected_names = ("Law", "Norms")
        assert merged_object.name in expected_names

        expected_aliases = {"law", "legal", "laws", "norms", "norm"}
        actual_aliases = set(merged_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases

    def test_preserves_related_content_for_authors(self):
        # Arrange - create topics and related content
        jane = Author.objects.create_with_aliases(name="Jane", aliases=["janet", "jan"])
        norms = Author.objects.create_with_aliases(name="Oscar", aliases=["osc"])

        now = datetime.datetime.now()
        video = ContentItem.objects.create(title="Video Item", publish_date=now)
        audio = ContentItem.objects.create(title="Audio Item", publish_date=now)
        text = ContentItem.objects.create(title="Text Item", publish_date=now)

        jane.content.add(video, audio)
        norms.content.add(text)

        # Act
        merged_object = Author.objects.all().merge_objects()

        # Assert
        assert not Author.objects.filter(pk__in=[jane.pk, norms.pk])

        expected_content = {video, audio, text}
        assert set(merged_object.content.all()) == expected_content

        expected_names = ("Jane", "Oscar")
        assert merged_object.name in expected_names

        expected_aliases = {"jane", "janet", "jan", "oscar", "osc"}
        actual_aliases = set(merged_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases


@pytest.mark.django_db
class TestConvertObject:
    def test_preserves_related_content(self):
        # Arrange - create topic and related content
        law_topic = Topic.objects.create_with_aliases(
            name="Law", description="A short description", aliases=["legal", "laws"]
        )

        now = datetime.datetime.now()
        video = ContentItem.objects.create(title="Video Item", publish_date=now)
        audio = ContentItem.objects.create(title="Audio Item", publish_date=now)
        text = ContentItem.objects.create(title="Text Item", publish_date=now)

        law_topic.content.add(video, audio, text)

        # Act
        converted_object = law_topic.convert_object(Idea)

        # Assert
        with pytest.raises(Topic.DoesNotExist):
            law_topic.refresh_from_db()

        expected_content = {video, audio, text}
        assert set(converted_object.content.all()) == expected_content

        assert converted_object.name == "Law"
        assert converted_object.description == "A short description"

        expected_aliases = {"law", "legal", "laws"}
        actual_aliases = set(converted_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases

    def test_can_convert_topic_to_author(self):
        # Arrange
        example_topic = Topic.objects.create_with_aliases(
            name="Example", description="A short description", aliases=["test"]
        )

        # Act
        converted_object = example_topic.convert_object(Author)

        # Assert
        with pytest.raises(Topic.DoesNotExist):
            example_topic.refresh_from_db()

        assert converted_object.name == "Example"
        assert converted_object.description is None

        expected_aliases = {"example", "test"}
        actual_aliases = set(converted_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases

    @pytest.mark.parametrize(
        "topic_name,aliases",
        [("Law", []), ("law", []), ("Norms", ["law"]), ("Norms", ["legal"])],
    )
    def test_fails_when_alias_already_exists(self, topic_name, aliases):
        # Arrange
        Idea.objects.create_with_aliases(name="Law", aliases=["legal", "laws"])
        law_topic = Topic.objects.create_with_aliases(name=topic_name, aliases=aliases)

        # Act & Assert
        with pytest.raises(IntegrityError):
            law_topic.convert_object(Idea)

        try:
            Topic.objects.get(pk=law_topic.pk)
        except Topic.DoesNotExist:
            pytest.fail("Topic was deleted during failed conversion.")

    def test_can_convert_object_without_description(self):
        law_tag = Tag.objects.create_with_aliases(name="Law", aliases=["legal", "laws"])

        converted_object = law_tag.convert_object(Idea)

        # Assert
        with pytest.raises(Tag.DoesNotExist):
            law_tag.refresh_from_db()

        assert converted_object.name == "Law"
        assert converted_object.description == ""

        expected_aliases = {"law", "legal", "laws"}
        actual_aliases = set(converted_object.aliases.values_list("text", flat=True))
        assert actual_aliases == expected_aliases
