# -*- coding: utf-8 -*-
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0008_auto_20180215_1445'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

