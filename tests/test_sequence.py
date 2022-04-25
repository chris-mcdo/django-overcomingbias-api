import datetime

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from obapi import utils
from obapi.models import (AudioContentItem, Sequence, TextContentItem,
                          VideoContentItem)


@pytest.fixture
def james():
    return User.objects.create_user("James", "james@example.com", "jamespassword")


@pytest.fixture
def alice():
    return User.objects.create_user("Alice", "alice@example.com", "alicepassword")


@pytest.mark.django_db
class TestCreateSequence:
    def test_can_create_empty_sequence(self, james):
        # Arrange
        seq_title = "Empty Sequence"
        # Act
        james.sequences.create(title=seq_title, description="Description")
        # Assert
        seq = james.sequences.get(title=seq_title)
        assert seq.slug == utils.slugify(seq_title)
        assert not seq.items.all().exists()

        # Act - modify title
        new_title = "New Title"
        seq.title = new_title
        seq.save()
        assert seq.slug == utils.slugify(new_title)

    def test_can_create_normal_sequence(self, james, alice):
        # Arrange
        now = datetime.datetime.now()
        video = VideoContentItem.objects.create(title="Video Item", publish_date=now)
        audio = AudioContentItem.objects.create(title="Audio Item", publish_date=now)
        text = TextContentItem.objects.create(title="Text Item", publish_date=now)
        seq_title = "Example Sequence"

        # Act - create basic sequence
        seq = james.sequences.create(title=seq_title)
        seq.items.add(video, audio, text)

        # Assert
        seq = Sequence.objects.get(title=seq_title)
        assert seq.title == seq_title
        assert seq.items.count() == 3

        # Act - change user
        seq.owner = alice
        seq.save()

        # Assert
        seq = Sequence.objects.get(title=seq_title)
        assert seq.owner.username == "Alice"

        # Act - delete the user
        alice.delete()
        del alice

        # Assert
        assert not Sequence.objects.filter(title=seq_title).exists()


@pytest.mark.django_db
class TestSlugUniquenessIsEnforced:
    def test_different_users_can_use_same_slug(self, james, alice):
        # Act and assert - create sequences
        james_seq = james.sequences.create(title="Fake Sequence")
        try:
            alice_seq = alice.sequences.create(title="Fake Sequence")
        except IntegrityError:
            pytest.fail("IntegrityError raised when creating fake sequence.")

        assert james_seq.slug == alice_seq.slug
        try:
            alice_seq.full_clean()
        except ValidationError:
            pytest.fail("ValidationError raised when validating fake sequence.")

    def test_duplicate_slug_does_not_save(self, james):
        # Act & Assert - sequence with owner
        james.sequences.create(title="Example Sequence")
        with pytest.raises(IntegrityError):
            james.sequences.create(title="example-sequence")

    def test_duplicate_slug_does_not_validate(self, james):
        # Act & Assert
        james.sequences.create(title="Example Sequence")
        seq2 = Sequence(title="example-sequence", owner=james)
        with pytest.raises(ValidationError):
            seq2.full_clean()
