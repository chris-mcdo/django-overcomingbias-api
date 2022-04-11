import pytest
from django.db import IntegrityError
from obapi.models import Idea, Topic


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
