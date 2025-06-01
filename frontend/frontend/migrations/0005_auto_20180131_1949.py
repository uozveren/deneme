# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_feed_edited'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postfield',
            name='field',
        ),
        migrations.RemoveField(
            model_name='postfield',
            name='post',
        ),
        migrations.DeleteModel(
            name='PostField',
        ),
    ]
