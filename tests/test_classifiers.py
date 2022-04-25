import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from obapi.models import Idea, Topic
from obapi.models.classifiers import IdeaAlias, TopicAlias


@pytest.mark.django_db
class TestCreateAliasedModel:
    def test_create_valid_topic(self):
        # Act
        Topic.objects.create(name="Law&Øther", description="Law and other topics.")

        # Assert
        obj = Topic.objects.get(name="Law&Øther")
        assert obj.name == "Law&Øther"
        assert obj.get_slug() == "law-other"
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
        assert obj.get_slug() == obj.name
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
        assert example.get_slug() == new_slug

    def test_can_create_another_object_type_with_same_name(self):
        # Act
        topic = Topic.objects.create(name="Duplicated", description="A duplicate.")
        idea = Idea.objects.create(name="Duplicated", description="A duplicate.")

        # Assert
        assert topic.name == idea.name
        assert topic.get_slug() == idea.get_slug()
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
class TestValidateUniqueAlias:
    def test_succeeds_for_unique_aliases(self):
        # Arrange
        law = Topic.objects.create(name="Law", description="About law.")
        law.aliases.create(text="Legal")
        norms = Topic.objects.create(name="Norms", description="About norms.")
        social = TopicAlias(text="Social Norms", owner=norms)

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
        law_topic.aliases.create(text="Rules")
        norms_idea = Idea.objects.create(name="Norms", description="About norms.")
        rules = IdeaAlias(text="Rules", owner=norms_idea)

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
