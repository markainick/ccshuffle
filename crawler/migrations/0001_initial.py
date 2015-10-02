# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ccshuffle.serialize
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlingProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=100)),
                ('execution_date', models.DateTimeField(default=datetime.datetime.now)),
                ('status', models.CharField(max_length=100)),
                ('exception', models.CharField(blank=True, max_length=500, null=True)),
            ],
            bases=(models.Model, ccshuffle.serialize.SerializableModel),
        ),
    ]
