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
        raise NotImplementedError('The function from_serialized of %s' % cls.__class__.__name__)


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
        """
        Checks if the artist has a jamendo id (profile).

        :return: True, if the artist has a jamendo id, otherwise False.
        """
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
        elif isinstance(obj, (dict, set)):
            try:
                aid = (int(obj['id']) if obj['id'] else None)
                jamendo_id = (int(obj['jamendo_id']) if obj['jamendo_id'] else None)
                return cls(id=aid, name=obj['name'], abstract=obj['abstract'], website=obj['website'],
                           city=obj['city'], country_code=obj['country_code'], jamendo_id=jamendo_id)
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
    cover = models.URLField(blank=False, null=True)
    release_date = models.DateField(blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def is_on_jamendo(self):
        """
        Checks if the album has a jamendo id (profile).

        :return: True, if the album has a jamendo id, otherwise False.
        """
        return self.jamendo_id is not None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'cover': self.cover,
            'release_date': self.release_date,
            'jamendo_id': self.jamendo_id,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                aid = (int(obj['id']) if obj['id'] else None)
                artist = (Artist.from_serialized(obj['artist']) if obj['artist'] else None)
                release_date = obj['release_date']
                if isinstance(release_date, str):
                    release_date = datetime.strptime(obj['release_date'], '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(release_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
                jamendo_id = (int(obj['jamendo_id']) if obj['jamendo_id'] else None)
                return cls(id=aid, name=obj['name'], artist=artist, cover=obj['cover'], release_date=release_date,
                           jamendo_id=jamendo_id)
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
                tid = (int(obj['id']) if obj['id'] else None)
                return cls(id=tid, name=obj['name'])
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


class License(models.Model, ModelSerializable):
    """ This class represents a license. """
    CC_BY = 'CC-BY'
    CC_BY_SA = 'CC-BY-SA'
    CC_BY_ND = 'CC-BY-ND'
    CC_BY_NC = 'CC-BY-NC'
    CC_BY_NC_SA = 'CC-BY-NC-SA'
    CC_BY_NC_ND = 'CC-BY-NC-ND'

    LICENSE_TYPE = (
        (CC_BY, 'Attribution'),
        (CC_BY_SA, 'Attribution-ShareAlike'),
        (CC_BY_ND, 'Attribution-NoDerivs'),
        (CC_BY_NC, 'Attribution-NonCommercial'),
        (CC_BY_NC_SA, 'Attribution-NonCommercial-ShareAlike'),
        (CC_BY_NC_ND, 'Attribution-NonCommercial-NoDerivs'),
    )

    LICENSE_WEB_LINK = {
        CC_BY: 'http://creativecommons.org/licenses/by/4.0/',
        CC_BY_SA: 'http://creativecommons.org/licenses/by-sa/4.0/',
        CC_BY_ND: 'http://creativecommons.org/licenses/by-nd/4.0/',
        CC_BY_NC: 'http://creativecommons.org/licenses/by-nc/4.0/',
        CC_BY_NC_SA: 'http://creativecommons.org/licenses/by-nc-sa/4.0/',
        CC_BY_NC_ND: 'http://creativecommons.org/licenses/by-nc-nd/4.0/',
    }

    type = models.CharField(max_length=15, choices=LICENSE_TYPE, blank=False)

    @property
    def name(self):
        """
        Returns the human readable name of the license.

        :return: the human readable name of the license.
        """
        if self.type in (entry[0] for entry in self.LICENSE_TYPE):
            return (entry[1] for entry in self.LICENSE_TYPE if entry[0] == self.type)
        else:
            raise ValueError('The license type is unknown.')

    @property
    def web_link(self):
        """
        Returns the web link to the license.

        :return: the web link to the license.
        """
        if self.type in self.LICENSE_WEB_LINK:
            return self.LICENSE_WEB_LINK[self.type]
        else:
            raise ValueError('The license type is unknown.')

    def serialize(self):
        return {
            'type': self.type,
            'name': self.name,
            'link': self.web_link,
        }

    def from_serialized(cls, obj):
        pass

    def __str__(self):
        return '%s (Link: %s)' % (self.name, self.web_link)


class Song(models.Model, ModelSerializable):
    """ This class represents the model for songs. Songs can be associated with an album or not (f.e. a single). """
    name = models.CharField(max_length=250, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    album = models.ForeignKey(Album, blank=True, null=True, related_name='song')
    cover = models.URLField(blank=False, null=True)
    duration = models.IntegerField(blank=True, default=None, null=True)
    tags = models.ManyToManyField(Tag)
    release_date = models.DateField(blank=True, default=None, null=True)

    jamendo_id = models.IntegerField(blank=True, unique=True, null=True)

    def sources(self, **source_fields):
        """
        Returns the sources of the song.

        :param source_fields: the optional fields for filtering the results.
        :return: the list of sources.
        """
        if self.id is None:
            raise ValueError('The song must be saved to call this method.')
        return list(Source.objects.filter(song=self, **source_fields))

    def is_on_jamendo(self):
        """
        Checks if the song has a jamendo id (profile).

        :return: True, if the song has a jamendo id, otherwise False.
        """
        return self.jamendo_id is not None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'album': self.album,
            'cover': self.cover,
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
                sid = (int(obj['id']) if obj['id'] else None)
                artist = (Artist.from_serialized(obj['artist']) if obj['artist'] else None)
                album = (Album.from_serialized(obj['album']) if obj['album'] else None)
                jamendo_id = (int(obj['jamendo_id']) if obj['jamendo_id'] else None)
                song = cls(id=sid, name=obj['name'], artist=artist, album=album, cover=obj['cover'],
                           duration=int(obj['duration']), release_date=release_date, jamendo_id=jamendo_id)
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


class Source(models.Model, ModelSerializable):
    """ This class represents a source of a song. (f.e. stream or download link) """

    TYPE_DOWNLOAD = 'D'
    TYPE_STREAM = 'S'

    CODEC_MP3 = 'MP3'
    CODEC_OGG = 'OGG'
    CODEC_FLAC = 'FLAC'
    CODEC_UNKNOWN = 'UNK'

    SOURCE_TYPE = (
        (TYPE_DOWNLOAD, 'Download'),
        (TYPE_STREAM, 'Stream'),
    )

    CODEC_TYPE = (
        (CODEC_MP3, 'MP3'),
        (CODEC_OGG, 'OGG'),
        (CODEC_FLAC, 'FLAC'),
        (CODEC_UNKNOWN, 'Unknown Codec')
    )

    type = models.CharField(choices=SOURCE_TYPE, max_length=2, blank=False)
    link = models.URLField(blank=False)
    song = models.ForeignKey(Song, blank=False)
    codec = models.CharField(choices=CODEC_TYPE, max_length=4, blank=False)

    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'link': self.link,
            'song_id': self.song.id,
            'codec': self.codec,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                sid = (int(obj['id']) if obj['id'] else None)
                song = None
                if obj['song_id']:
                    song_query_set = Song.objects.filter(id=int(obj['song_id']))
                    song = (song_query_set.first() if song_query_set.exists() else None)
                return cls(id=sid, type=obj['type'], link=obj['link'], song=song, codec=obj['codec'])
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.type == other.type and self.link == other.link and self.codec == other.codec
        else:
            return False

    def __hash__(self):
        return hash(self.type) ^ hash(self.link) ^ hash(self.codec)

    def __str__(self):
        return 'Song: %s Type: %s Link: %s (Codec: %s)' % (repr(self.song), self.type, self.link, self.codec)


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
