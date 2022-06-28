import datetime
import random

import pytest
from obapi.models import OBContentItem


class TestFindByURL:
    pass


@pytest.mark.django_db
def test_update_last_edit_dates(random_obcontentitems):
    items = random_obcontentitems(5)
    true_edit_dates = [item.edit_date for item in items]
    for item in items:
        item.edit_date = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)

    item_ids = [item.item_id for item in items]
    items_queryset = OBContentItem.objects.filter(item_id__in=item_ids)

    items_queryset.update_last_edit_dates()

    # Assert
    for i, item in enumerate(items):
        item.refresh_from_db()
        assert item.edit_date == true_edit_dates[i]


@pytest.mark.django_db
def test_download_new_items(obcontent_edit_dates):
    # Arrange - How many posts to run this test on?
    posts_to_create = 5
    # Arrange - select most recent posts
    sorted_edit_dates = dict(
        sorted(obcontent_edit_dates.items(), key=lambda item: item[1], reverse=True)
    )
    edit_date_iterator = iter(sorted_edit_dates.items())
    latest_posts = [next(edit_date_iterator) for i in range(0, posts_to_create)]

    # Act - create a post from a short while back
    oldest_item_id = latest_posts[posts_to_create - 1][0]
    oldest_item_edit_date = latest_posts[posts_to_create - 1][1]
    created_item = OBContentItem.objects.create_item(oldest_item_id)

    # Assert - was it created ok
    assert created_item.item_id == oldest_item_id
    assert created_item.edit_date == oldest_item_edit_date
    assert OBContentItem.objects.count() == 1

    # Act - call download_new_items
    original_download_timestamp = created_item.download_timestamp
    created_count = OBContentItem.objects.download_new_items()

    # Assert - items were created ok
    assert created_count == posts_to_create - 1
    assert OBContentItem.objects.count() == posts_to_create
    assert (
        OBContentItem.objects.get(item_id=oldest_item_id).download_timestamp
        == original_download_timestamp
    )


@pytest.mark.django_db
def test_bulk_create_items(obcontent_edit_dates):
    # Arrange - configure test settings
    batch_size = 2
    posts_to_create = 5

    # Arrange - collect sample post IDs
    all_item_ids = [key for key, value in obcontent_edit_dates.items()]
    sample_ids = random.sample(all_item_ids, posts_to_create)

    # Act - create items
    created_count = OBContentItem.objects.bulk_create_items(
        sample_ids, batch_size=batch_size
    )

    # Assert - items created correctly
    all_items = OBContentItem.objects.all()
    assert all_items.count() == created_count

    if created_count > batch_size:
        assert (
            all_items.latest("download_timestamp").download_timestamp
            > all_items.earliest("download_timestamp").download_timestamp
        )
