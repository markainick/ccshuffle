# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ccshuffle.serialize


class Migration(migrations.Migration):

    dependencies = [
        ('shuffle', '0003_delete_crawlingprocess'),
    ]

    operations = [
        migrations.CreateModel(
            name='JamendoAlbumProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('jamendo_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=256)),
                ('cover', models.URLField(null=True, blank=True)),
                ('external_link', models.URLField(null=True, blank=True)),
            ],
            bases=(models.Model, ccshuffle.serialize.SerializableModel),
        ),
        migrations.CreateModel(
            name='JamendoArtistProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('jamendo_id', models.IntegerField()),
                ('name', models.CharField(max_length=256)),
                ('image', models.URLField(default=None, null=True, blank=True)),
                ('external_link', models.URLField(default=None, null=True, blank=True)),
            ],
            bases=(models.Model, ccshuffle.serialize.SerializableModel),
        ),
        migrations.CreateModel(
            name='JamendoSongProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('jamendo_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=256)),
                ('external_link', models.URLField(default=None, null=True, blank=True)),
                ('cover', models.URLField(default=None, null=True, blank=True)),
            ],
            bases=(models.Model, ccshuffle.serialize.SerializableModel),
        ),
        migrations.CreateModel(
            name='JamendoSongStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SongStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='album',
            name='jamendo_id',
        ),
        migrations.RemoveField(
            model_name='artist',
            name='jamendo_id',
        ),
        migrations.RemoveField(
            model_name='song',
            name='jamendo_id',
        ),
        migrations.AlterField(
            model_name='artist',
            name='website',
            field=models.URLField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='jamendo_profile',
            field=models.ForeignKey(default=None, null=True, to='shuffle.JamendoAlbumProfile', blank=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='jamendo_profile',
            field=models.ForeignKey(default=None, null=True, to='shuffle.JamendoArtistProfile', blank=True),
        ),
        migrations.AddField(
            model_name='song',
            name='jamendo_profile',
            field=models.ForeignKey(default=None, null=True, to='shuffle.JamendoSongProfile', blank=True),
        ),
    ]
