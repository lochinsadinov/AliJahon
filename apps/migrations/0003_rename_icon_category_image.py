# Generated by Django 5.1.3 on 2024-11-15 05:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_rename_image_category_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='icon',
            new_name='image',
        ),
    ]
