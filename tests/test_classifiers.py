import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from obapi.models import Idea, Topic
from obapi.models.classifiers import IdeaAlias, TopicAlias


@pytest.mark.django_db
class TestCreateAliasedModel:
    def test_create_valid_object_with_two_aliases(self):
        # Act
        Topic.objects.create(name="Law&Øther", description="Law and other topics.")

        # Assert
        obj = Topic.objects.get(name="Law&Øther")
        assert obj.name == "Law&Øther"
        assert obj.slug == "law-other"
        assert obj.description == "Law and other topics."

        obj_aliases = obj.aliases.all()
        expected_aliases = {"law-other", "Law&Øther"}
        assert set(obj_aliases.values_list("text", flat=True)) == expected_aliases
        assert all(obj_aliases.values_list("protected", flat=True))

    def test_create_valid_model_with_one_alias(self):
        # Act
        Topic.objects.create(name="topic-two")  # slug is same as name

        # Assert
        obj = Topic.objects.get(name="topic-two")
        assert obj.name == "topic-two"
        assert obj.slug == obj.name
        assert obj.description == ""

        obj_aliases = obj.aliases.all()
        expected_aliases = {"topic-two"}
        assert set(obj_aliases.values_list("text", flat=True)) == expected_aliases
        assert obj_aliases[0].protected

    @pytest.mark.parametrize(
        "new_name,new_slug",
        [
            ("Law&Other", "law-other"),
            ("law other", "law-other"),
            ("law-other", "law-other"),
            ("LawOther", "lawother"),
        ],
    )
    def test_change_object_name(self, new_name, new_slug):
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
        assert set(topic.aliases.values_list("text", flat=True)) == set(
            idea.aliases.values_list("text", flat=True)
        )

    def test_cannot_duplicate_names_or_aliases(self):
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
        assert social.validate_unique() is None  # not yet saved
        social.save()
        assert social.validate_unique() is None

    def test_succeeds_when_another_object_type_has_same_alias(self):
        # Arrange
        law_topic = Topic.objects.create(name="Law", description="About law.")
        law_topic.aliases.create(text="Rules")
        norms_idea = Idea.objects.create(name="Norms", description="About norms.")
        rules = IdeaAlias(text="Rules", owner=norms_idea)

        # Act & assert
        assert rules.validate_unique() is None  # not yet saved
        rules.save()
        assert rules.validate_unique() is None

    @pytest.mark.parametrize("alias_text", ["Law", "law", "Rules", "rulEs"])
    def test_fails_with_duplicate_aliases(self, alias_text):
        # Arrange
        law = Topic.objects.create(name="Law", description="About law.")
        law.aliases.create(text="Rules")
        norms = Topic.objects.create(name="Norms", description="About norms.")

        # Assert
        norms_alias = TopicAlias(text=alias_text, owner=norms)
        with pytest.raises(ValidationError):
            norms_alias.validate_unique()
