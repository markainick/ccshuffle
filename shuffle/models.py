
#   COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

from django.db import models


class Artist(models.Model):
    """ This class represents the model for artists. """
    name = models.CharField(max_length=250, blank=False)
    abstract = models.CharField(max_length=250, blank=True, default=None)
    website = models.URLField(blank=True, default=None)
    city = models.CharField(max_length=250, blank=True, default=None)
    country_code = models.CharField(max_length=250, blank=True, default=None)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def has_jamendo_profile(self):
        return self.jamendo_id is not None

    def __str__(self):
        return self.name


class Album(models.Model):
    """ This class represents the model for albums. An album contains typically more than one song. """
    name = models.CharField(max_length=512, blank=False)
    artist = models.ForeignKey(Artist, blank=False)
    release_date = models.DateTimeField(blank=True, default=None)

    def __str__(self):
        return self.name

class JamendoAlbum(Album):
    pass


class SoundcloudAlbum(Album):
    pass


class Tag(models.Model):
    """ This class represents a tag, which is used to describe the music (f.e. genres). """
    name = models.CharField(max_length=250, blank=False, unique=True)


class Song(models.Model):
    """ This class represents the model for songs. Songs can be associated with an album or not (f.e. a single). """
    name = models.CharField(max_length=250, blank=False)
    album = models.ForeignKey(Album, default=None, related_name='songs')
    duration = models.IntegerField(blank=True, default=None)
    album = models.ForeignKey(Album, blank=True, default=None, null=True)
    tags = models.ManyToManyField(Tag)
    release_date = models.DateTimeField(blank=True, default=None)

    jamendo_id = models.IntegerField(blank=True, unique=False, null=True)

    def __str__(self):
        return self.name + (" (Album" + self.album + ")" if self.album is not None else "")
