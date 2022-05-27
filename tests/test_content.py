import datetime

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
