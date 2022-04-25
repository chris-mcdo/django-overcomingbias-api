# Generated by Django 4.0.3 on 2022-04-25 15:04

import obapi.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("obapi", "0003_remove_authoralias_authoralias_is_unique_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authoralias",
            name="text",
            field=obapi.modelfields.SimpleSlugField(
                help_text="Alias text.", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="ideaalias",
            name="text",
            field=obapi.modelfields.SimpleSlugField(
                help_text="Alias text.", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="sequence",
            name="slug",
            field=obapi.modelfields.SimpleSlugField(
                editable=False, max_length=100, null=True
            ),
        ),
        migrations.AlterField(
            model_name="tagalias",
            name="text",
            field=obapi.modelfields.SimpleSlugField(
                help_text="Alias text.", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="topicalias",
            name="text",
            field=obapi.modelfields.SimpleSlugField(
                help_text="Alias text.", max_length=100, unique=True
            ),
        ),
    ]