# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
       ('shuffle', '0002_fixtures'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CrawlingProcess',
        ),
    ]
