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
from datetime import datetime
from abc import abstractmethod
from django.core.serializers.json import DjangoJSONEncoder


class ModelSerializable(object):
    """ This class represents json models that have the function 'serializable' that returns a serializable object.  """

    @abstractmethod
    def serializable(self, obj):
        raise NotImplementedError('The function serializable of %s' % self.__class__.__name__)


class JSONModelEncoder(DjangoJSONEncoder):
    """  This class represents a json encoder for the models, which are instance of the ModelSerializable class."""

    def default(self, o):
        if o is None:
            return ''
        elif isinstance(o, (str, int, float)):
            return str(o)
        elif isinstance(o, ModelSerializable):
            so = o.serializable()
            r = dict()
            if isinstance(so, (dict, set)):
                for key in so:
                    r[str(key)] = self.default(so[key])
                return r
            elif isinstance(so, (list, tuple)):
                l = []
                for value in so:
                    l.append(self.default(value))
                return l
            else:
                return super(type(self), self).default(so)
        else:
            return super(type(self), self).default(o)


class Artist(models.Model):
    """ This class represents the model for artists. """
    name = models.CharField(max_length=250, blank=False)
    abstract = models.CharField(max_length=250, blank=True, default=None, null=True)
    website = models.URLField(blank=True, default=None, null=True)
    city = models.CharField(max_length=250, blank=True, default=None, null=True)
    country_code = models.CharField(max_length=250, blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        return self.jamendo_id is not None

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo() and other.is_on_jamendo() else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Album(models.Model):
    """ This class represents the model for albums. An album contains typically more than one song. """
    name = models.CharField(max_length=512, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    release_date = models.DateField(blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        return self.jamendo_id is not None

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and self.artist == other.artist and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo() and other.is_on_jamendo() else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name) ^ hash(self.artist)

    def __str__(self):
        return self.name + (' (Artist: %s) ' % self.artist if self.artist else '')


class Tag(models.Model):
    """ This class represents a tag, which is used to describe the music (f.e. genres). """
    name = models.CharField(max_length=250, blank=False, unique=True)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name is other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Song(models.Model):
    """ This class represents the model for songs. Songs can be associated with an album or not (f.e. a single). """
    name = models.CharField(max_length=250, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    album = models.ForeignKey(Album, blank=True, null=True, related_name='songs')
    duration = models.IntegerField(blank=True, default=None)
    tags = models.ManyToManyField(Tag)
    release_date = models.DateField(blank=True, default=None)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        return self.album is not None

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and self.artist == other.artist and self.album == other.album and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo() and other.is_on_jamendo() else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name) ^ hash(self.artist) ^ hash(self.album)

    def __str__(self):
        return self.name + (' (Artist: %s) ' % self.artist if self.artist else '') + (
            ' (Album: %s)' % self.album if self.album else '')


class CrawlingProcess(models.Model, ModelSerializable):
    """ This class represents planned, executed or failed crawling processes. """

    Service_Jamendo = 'Jamendo'
    Service_Soundcloud = 'Soundcloud'
    Service_CCMixter = 'CCMixter'
    Service_General = 'GENERAL'

    Status_Planned = 'Planned'
    Status_Running = 'Running'
    Status_Finished = 'Finished'
    Status_Failed = 'Failed'

    service = models.CharField(max_length=100, blank=False)
    execution_date = models.DateTimeField(blank=False, default=datetime.now)
    status = models.CharField(max_length=100, blank=False)
    exception = models.CharField(max_length=500, blank=True, null=True)

    def serializable(self):
        return {'service': str(self.service),
                'execution_date': self.execution_date,
                'status': str(self.status),
                'exception': str(self.exception)
                }

    def __str__(self):
        return '%s (%s - %s)' % (self.execution_date, self.service, self.status)
