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


class DeserializableException(Exception):
    """ This exception will be thrown, if the serialized representation can't be parsed correctly."""
    pass


class ModelSerializable(object):
    """ This class represents json models that have the function 'serializable' that returns a serializable object.  """

    @abstractmethod
    def serialize(self):
        """
        Serializes this object so that it f.e. can be converted to JSON.

        :return:the serialized object.
        """
        raise NotImplementedError('The function serialize of %s' % self.__class__.__name__)

    @classmethod
    @abstractmethod
    def from_serialized(cls, obj):
        """
        Parses the serialized representation of the object of this class and returns a object of this class. Throws a
        DeserializableException, if the representation can not be pared.

        :param obj: the serialized representation of the object, which shall be parsed.
        :return: the object of this class.
        """
        raise NotImplementedError('The function from_serialized of %s' % self.__class__.__name__)


class JSONModelEncoder(DjangoJSONEncoder):
    """  This class represents a json encoder for the models, which are instance of the ModelSerializable class."""

    def default(self, o):
        if o is None:
            return ''
        elif isinstance(o, (str, int, float)):
            return str(o)
        elif isinstance(o, (dict, set)):
            return {key: self.default(o[key]) for key in o}
        elif isinstance(o, (list, tuple)):
            return [self.default(entry) for entry in o]
        elif isinstance(o, ModelSerializable):
            # Serialize if the object is serializable.
            return self.default(o.serialize())
        else:
            return super(type(self), self).default(o)


class Artist(models.Model, ModelSerializable):
    """ This class represents the model for artists. """
    name = models.CharField(max_length=250, blank=False)
    abstract = models.CharField(max_length=250, blank=True, default=None, null=True)
    website = models.URLField(blank=True, default=None, null=True)
    city = models.CharField(max_length=250, blank=True, default=None, null=True)
    country_code = models.CharField(max_length=250, blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        return self.jamendo_id is not None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'abstract': self.abstract,
            'website': self.website,
            'city': self.city,
            'country_code': self.country_code,
            'jamendo_id': self.jamendo_id,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                return cls(id=int(obj['id']), name=obj['name'], abstract=obj['abstract'], website=obj['website'],
                           city=obj['city'], country_code=obj['country_code'], jamendo_id=int(obj['jamendo_id']))
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

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


class Album(models.Model, ModelSerializable):
    """ This class represents the model for albums. An album contains typically more than one song. """
    name = models.CharField(max_length=512, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    release_date = models.DateField(blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        return self.jamendo_id is not None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'release_date': self.release_date,
            'jamendo_id': self.jamendo_id,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                release_date = obj['release_date']
                if isinstance(release_date, str):
                    release_date = datetime.strptime(obj['release_date'], '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(release_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
                return cls(id=int(obj['id']), name=obj['name'], artist=Artist.from_serialized(obj['artist']),
                           release_date=release_date, jamendo_id=int(obj['jamendo_id']))
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

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


class Tag(models.Model, ModelSerializable):
    """ This class represents a tag, which is used to describe the music (f.e. genres). """
    name = models.CharField(max_length=250, blank=False, unique=True)

    class Meta(object):
        ordering = ['name']

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                return cls(id=int(obj['id']), name=obj['name'])
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Song(models.Model, ModelSerializable):
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

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'tags': list(self.tags.all()),
            'release_date': self.release_date,
            'jamendo_id': self.jamendo_id,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                release_date = obj['release_date']
                if isinstance(release_date, str):
                    release_date = datetime.strptime(obj['release_date'], '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(release_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
                song = cls(id=int(obj['id']), name=obj['name'], artist=Artist.from_serialized(obj['artist']),
                           album=Album.from_serialized(obj['album']), duration=int(obj['duration']),
                           release_date=release_date, jamendo_id=int(obj['jamendo_id']))
                if obj['tags']:
                    song.tags.add(*[Tag.from_serialized(entry) for entry in obj['tags']])
                return song
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

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
            ' (Album: %s) ' % self.album if self.album else '')


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

    def serialize(self):
        return {
            'service': self.service,
            'execution_date': self.execution_date,
            'status': self.status,
            'exception': self.exception,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                execution_date = obj['execution_date']
                if isinstance(execution_date, str):
                    execution_date = datetime.strptime(obj['execution_date'], '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(execution_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
                return cls(service=obj['service'], execution_date=execution_date, status=obj['status'],
                           exception=obj['exception'])
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

    def __str__(self):
        return '%s (%s - %s)' % (self.execution_date, self.service, self.status)
