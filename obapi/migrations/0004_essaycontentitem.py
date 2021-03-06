# Generated by Django 4.0.3 on 2022-07-07 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("obapi", "0003_alter_contentitem_title_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EssayContentItem",
            fields=[
                (
                    "textcontentitem_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="obapi.textcontentitem",
                    ),
                ),
                (
                    "item_id",
                    models.CharField(
                        help_text='Essay string identifier. E.g. "Varytax"',
                        max_length=300,
                        unique=True,
                        verbose_name="string ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "essay",
            },
            bases=("obapi.textcontentitem",),
        ),
    ]
