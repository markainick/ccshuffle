# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shuffle.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('cover', models.URLField(null=True)),
                ('release_date', models.DateField(blank=True, null=True, default=None)),
                ('jamendo_id', models.IntegerField(blank=True, null=True, unique=True)),
            ],
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('abstract', models.CharField(blank=True, null=True, max_length=250, default=None)),
                ('website', models.URLField(blank=True, null=True, default=None)),
                ('city', models.CharField(blank=True, null=True, max_length=250, default=None)),
                ('country_code', models.CharField(blank=True, null=True, max_length=250, default=None)),
                ('jamendo_id', models.IntegerField(blank=True, null=True, unique=True)),
            ],
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='CrawlingProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('service', models.CharField(max_length=100)),
                ('execution_date', models.DateTimeField(default=datetime.datetime.now)),
                ('status', models.CharField(max_length=100)),
                ('exception', models.CharField(blank=True, null=True, max_length=500)),
            ],
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('type', models.CharField(max_length=15, choices=[('CC-BY', 'Attribution'), ('CC-BY-SA', 'Attribution-ShareAlike'), ('CC-BY-ND', 'Attribution-NoDerivs'), ('CC-BY-NC', 'Attribution-NonCommercial'), ('CC-BY-NC-SA', 'Attribution-NonCommercial-ShareAlike'), ('CC-BY-NC-ND', 'Attribution-NonCommercial-NoDerivs')])),
            ],
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('cover', models.URLField(null=True)),
                ('duration', models.IntegerField(blank=True, null=True, default=None)),
                ('release_date', models.DateField(blank=True, null=True, default=None)),
                ('jamendo_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('album', models.ForeignKey(blank=True, null=True, related_name='song', to='shuffle.Album')),
                ('artist', models.ForeignKey(blank=True, null=True, to='shuffle.Artist')),
                ('license', models.ForeignKey(to='shuffle.License')),
            ],
            bases=(models.Model, shuffle.models.SerializableModel, shuffle.models.SearchableModel),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('type', models.CharField(max_length=2, choices=[('D', 'Download'), ('S', 'Stream')])),
                ('link', models.URLField()),
                ('codec', models.CharField(max_length=4, choices=[('MP3', 'MP3'), ('OGG', 'OGG'), ('FLAC', 'FLAC'), ('UNK', 'Unknown Codec')])),
                ('song', models.ForeignKey(to='shuffle.Song')),
            ],
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=250)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, shuffle.models.SerializableModel),
        ),
        migrations.AddField(
            model_name='song',
            name='tags',
            field=models.ManyToManyField(to='shuffle.Tag'),
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(blank=True, null=True, to='shuffle.Artist'),
        ),
    ]
