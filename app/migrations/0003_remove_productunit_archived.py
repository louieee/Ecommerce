# Generated by Django 5.1.2 on 2024-10-18 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_category_options_alter_productbatch_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productunit',
            name='archived',
        ),
    ]
