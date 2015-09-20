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
from django.db.models import Q, Count
from ccshuffle.serialize import SerializableModel, DeserializableException


class SearchableModel(object):
    @classmethod
    @abstractmethod
    def search(cls, phrase: str, tags: [str]) -> [models.Model]:
        """
        Searches for the model objects, which fulfill all or some search criteria.

        :param phrase: the phrase to search for.
        :param tags: the tags, which describes the model object.
        :return: the model objects, which fulfill all or some search criteria.
        """
        raise NotImplementedError('The function search of %s' % cls.__class__.__name__)


class JamendoArtistProfile(models.Model, SerializableModel):
    jamendo_id = models.IntegerField()
    name = models.CharField(max_length=256)
    image = models.URLField(blank=True, null=True, default=None)
    external_link = models.URLField(blank=True, null=True, default=None)

    def serialize(self):
        return {
            'id': self.id,
            'jamendo_id': self.jamendo_id,
            'name': self.name,
            'image': self.image,
            'external_link': self.external_link,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            aid = int(obj['id']) if 'id' in obj and obj['id'] is not None else None
            # Parses the jamendo id of the artist profile.
            jamendo_id = obj['jamendo_id'] if 'jamendo_id' in obj else None
            if jamendo_id is None:
                raise DeserializableException('The name of the artist profile must not be None.')
            # Parses the name, image and external link of the artist profile.
            name = obj['name'] if 'name' in obj else None
            image = obj['image'] if 'image' in obj else None
            external_link = obj['external_link'] if 'external_link' else None
            return JamendoArtistProfile(id=aid, name=name, jamendo_id=jamendo_id, image=image,
                                        external_link=external_link)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.jamendo_id == other.jamendo_id

    def __hash__(self):
        return hash(self.jamendo_id)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class Artist(models.Model, SerializableModel, SearchableModel):
    # Meta information of the album.
    name = models.CharField(max_length=250, blank=False)
    abstract = models.CharField(max_length=250, blank=True, default=None, null=True)
    website = models.URLField(blank=False, null=True, default=None)
    city = models.CharField(max_length=250, blank=True, default=None, null=True)
    country_code = models.CharField(max_length=250, blank=True, default=None, null=True)
    # Jamendo profile of the album.
    jamendo_profile = models.ForeignKey(JamendoArtistProfile, blank=True, null=True, default=None)

    @classmethod
    def search(cls, phrase: str, tags: [str]):
        raise NotImplementedError('The search of artists is not implemented.')

    @property
    def is_on_jamendo(self):
        """
        Checks if the artist has a jamendo id (profile).

        :return: True, if the artist has a jamendo id, otherwise False.
        """
        return self.jamendo_profile is not None

    @property
    def jamendo_id(self):
        """
        The id of the jamendo profile will be returned. If no jamendo profile exists, None will be returned.

        :return: the id of the jamendo profile or None if no jamendo profile exists.
        """
        return self.jamendo_profile.jamendo_id if self.is_on_jamendo else None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'abstract': self.abstract,
            'website': self.website,
            'city': self.city,
            'country_code': self.country_code,
            'jamendo_profile': self.jamendo_profile,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            aid = (int(obj['id']) if 'id' in obj and obj['id'] is not None else None)
            # Parses the name of the artist.
            name = obj['name'] if 'name' in obj else None
            if name is None:
                raise DeserializableException('The name of the artist must not be None.')
            # Parses the abstract of the artist.
            abstract = obj['abstract'] if 'abstract' in obj else None
            # Parses the location of the artist.
            website = obj['website'] if 'website' in obj else None
            city = obj['city'] if 'city' in obj else None
            country_code = obj['country_code'] if 'country_code' in obj else None
            # Parses the jamendo profile.
            jamendo_profile = None
            if 'jamendo_profile' in obj and obj['jamendo_profile'] is not None:
                jamendo_profile = JamendoArtistProfile.from_serialized(obj['jamendo_profile'])
            return cls(id=aid, name=name, abstract=abstract, city=city, country_code=country_code, website=website,
                       jamendo_profile=jamendo_profile)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo and other.is_on_jamendo else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class JamendoAlbumProfile(models.Model, SerializableModel):
    jamendo_id = models.IntegerField(unique=True, blank=False)
    name = models.CharField(max_length=256, blank=False)
    cover = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)

    @abstractmethod
    def serialize(self):
        return {
            'id': self.id,
            'jamendo_id': self.jamendo_id,
            'name': self.name,
            'cover': self.cover,
            'external_link': self.external_link,
        }

    @classmethod
    @abstractmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            aid = int(obj['id']) if 'id' in obj and obj['id'] is not None else None
            # Parses the jamendo id of the album profile.
            jamendo_id = obj['jamendo_id'] if 'jamendo_id' in obj else None
            if jamendo_id is None:
                raise DeserializableException('The name of the album profile must not be None.')
            # Parses the name, cover, external link of the album profile.
            name = obj['name'] if 'name' in obj else None
            cover = obj['cover'] if 'cover' in obj else None
            external_link = obj['external_link'] if 'external_link' in obj else None
            return JamendoAlbumProfile(id=aid, jamendo_id=jamendo_id, name=name, cover=cover,
                                       external_link=external_link)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.jamendo_id == other.jamendo_id

    def __hash__(self):
        return hash(self.jamendo_id)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class Album(models.Model, SerializableModel, SearchableModel):
    # Meta information of the album.
    name = models.CharField(max_length=512, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    cover = models.URLField(blank=False, null=True)
    release_date = models.DateField(blank=True, default=None, null=True)
    # Profiles of the album.
    jamendo_profile = models.ForeignKey(JamendoAlbumProfile, blank=True, null=True, default=None)

    @classmethod
    def search(cls, phrase: str, tags: [str]):
        raise NotImplementedError('The search of albums is not implemented.')

    @property
    def is_on_jamendo(self):
        """
        Checks if the album has a jamendo profile.

        :return: True, if the album has a jamendo profile, otherwise False.
        """
        return self.jamendo_profile is not None

    @property
    def jamendo_id(self):
        """
        The id of the jamendo profile will be returned. If no jamendo profile exists, None will be returned.

        :return: the id of the jamendo profile or None if no jamendo profile exists.
        """
        return self.jamendo_profile.jamendo_id if self.is_on_jamendo else None

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'cover': self.cover,
            'release_date': self.release_date,
            'jamendo_profile': self.jamendo_profile,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            # Parses the id of the album.
            aid = (int(obj['id']) if 'id' in obj and obj['id'] is not None else None)
            # Parses the name of the album.
            name = obj['name'] if 'name' in obj else None
            if name is None:
                raise DeserializableException('The name of the album must not be None.')
            # Parses the cover of the album.
            cover = obj['cover'] if 'cover' in obj else None
            # Parses the artist of the album.
            artist = (Artist.from_serialized(obj['artist']) if obj['artist'] else None)
            # Parses the release date of the album.
            release_date = obj['release_date'] if 'release_date' in obj else None
            if release_date is not None:
                if isinstance(release_date, str):
                    try:
                        release_date = datetime.strptime(obj['release_date'], '%Y-%m-%dT%H:%M:%S')
                    except Exception as e:
                        raise DeserializableException('The given release date can\'t be parsed. (%s)' % e.args[0])
                elif not isinstance(release_date, datetime):
                    raise DeserializableException(
                        'The given release date can\'t be parsed. %s unsupported.' % type(release_date))
            # Parses the jamendo profile of the album.
            jamendo_profile = None
            if 'jamendo_profile' in obj and obj['jamendo_profile'] is not None:
                jamendo_profile = JamendoAlbumProfile.from_serialized(obj['jamendo_profile'])
            return cls(id=aid, name=name, artist=artist, cover=cover, release_date=release_date,
                       jamendo_profile=jamendo_profile)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and self.artist == other.artist and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo and other.is_on_jamendo else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name) ^ hash(self.artist)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class Tag(models.Model, SerializableModel):
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
        elif isinstance(obj, dict):
            tid = (int(obj['id']) if 'id' in obj and obj['id'] is not None else None)
            name = obj['name'] if 'name' in obj else None
            return cls(id=tid, name=name)
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

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class License(models.Model, SerializableModel):
    CC_BY = 'CC-BY'
    CC_BY_SA = 'CC-BY-SA'
    CC_BY_ND = 'CC-BY-ND'
    CC_BY_NC = 'CC-BY-NC'
    CC_BY_NC_SA = 'CC-BY-NC-SA'
    CC_BY_NC_ND = 'CC-BY-NC-ND'
    CC_UNKNOWN = 'Unknown'

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
            return (entry[1] for entry in self.LICENSE_TYPE if entry[0] == self.type).__next__()
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
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'link': self.web_link,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            lid = int(obj['id']) if 'id' in obj and obj['id'] else None
            type = obj['type'] if 'type' in obj else None
            if type is None and type not in [entry[0] for entry in cls.LICENSE_TYPE]:
                raise DeserializableException(
                    'The given type \'%s\' of license is unknown. It must not be None.' % type)
            return cls(id=lid, type=type)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.type == other.type
        else:
            return False

    def __hash__(self):
        return hash(type)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class JamendoSongProfile(models.Model, SerializableModel):
    jamendo_id = models.IntegerField(unique=True, blank=False)
    name = models.CharField(max_length=256, blank=False)
    external_link = models.URLField(blank=True, default=None, null=True)
    cover = models.URLField(blank=True, default=None, null=True)

    def serialize(self):
        return {
            'id': self.id,
            'jamendo_id': self.jamendo_id,
            'name': self.name,
            'external_link': self.external_link,
            'cover': self.cover,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            # Parses the song id.
            pid = int(obj['id']) if 'id' in obj else None
            # Parses the name of the profile.
            name = obj['name'] if 'name' in obj else None
            # Parses the id of the jamendo profile.
            jamendo_id = int(obj['jamendo_id']) if 'jamendo_id' in obj else None
            if jamendo_id is None:
                raise DeserializableException('The jamendo id of the song profile must not be None.')
            # Parses the external link of the profile.
            external_link = obj['external_link'] if 'external_link' in obj else None
            # Parses the cover link of the profile.
            cover_link = obj['cover'] if 'cover' in obj else None
            return JamendoSongProfile(id=pid, jamendo_id=jamendo_id, name=name, external_link=external_link,
                                      cover=cover_link)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.jamendo_id == other.jamendo_id

    def __hash__(self):
        return hash(self.jamendo_id)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class Song(models.Model, SerializableModel, SearchableModel):
    # Meta information of the song.
    name = models.CharField(max_length=250, blank=False)
    artist = models.ForeignKey(Artist, blank=True, null=True)
    album = models.ForeignKey(Album, blank=True, null=True, related_name='song')
    cover = models.URLField(blank=False, null=True)
    license = models.ForeignKey(License, blank=False)
    duration = models.IntegerField(blank=True, default=None, null=True)
    tags = models.ManyToManyField(Tag)
    release_date = models.DateField(blank=True, default=None, null=True)
    # Profiles of the song.
    jamendo_profile = models.ForeignKey(JamendoSongProfile, blank=True, default=None, null=True)

    @classmethod
    def search(cls, phrase: str, tags: [str]):
        query = Q(name__icontains=phrase)
        if tags:
            tags_query = None
            for tag in tags:
                tags_query = (tags_query | Q(tags__name=tag) if tags_query else Q(tags__name=tag))
            query |= tags_query
        return Song.objects.filter(query).annotate(match_count=Count('id')).order_by('-match_count')

    @property
    def is_on_jamendo(self):
        """
        Checks if the song has a jamendo profile.

        :return: True, if the song has a jamendo profile, otherwise False.
        """
        return self.jamendo_profile is not None

    @property
    def jamendo_id(self):
        """
        The id of the jamendo profile will be returned. If no jamendo profile exists, None will be returned.

        :return: the id of the jamendo profile or None if no jamendo profile exists.
        """
        return self.jamendo_profile.jamendo_id if self.is_on_jamendo else None

    @property
    def all_tags(self):
        """
        Returns the tags of this song.

        :return: the tags of this song.
        """
        return self.tags.all()

    @property
    def tags_names(self):
        """
        Returns the name of the tags as list.

        :return: the name of the tags as list.
        """
        return [tag.name for tag in self.tags]

    def sources(self, **source_fields):
        """
        Returns the sources of the song.

        :param source_fields: the optional fields for filtering the results.
        :return: the list of sources.
        """
        if self.id is None:
            raise ValueError('The song must be saved to call this method.')
        return list(Source.objects.filter(song=self, **source_fields))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'album': self.album,
            'cover': self.cover,
            'license': self.license,
            'duration': self.duration,
            'tags': list(self.tags.all()),
            'release_date': self.release_date,
            'jamendo_profile': self.jamendo_profile,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, dict):
            # Parses the song id.
            sid = (int(obj['id']) if 'id' in obj else None)
            # Parses the name of the song.
            name = obj['name'] if 'name' in obj else None
            if name is None:
                raise DeserializableException('The name of the song must not be None.')
            # Parses the artist of the song.
            artist = Artist.from_serialized(obj['artist']) if 'artist' in obj and obj['artist'] is not None else None
            # Parses the album of the song.
            album = Album.from_serialized(obj['album']) if 'album' in obj and obj['album'] is not None else None
            # Parses the duration of the song.
            duration = int(obj['duration']) if 'duration' in obj and obj['duration'] is not None else None
            # Parses the release date of the song.
            release_date = None
            if 'release_date' in obj and obj['release_date']:
                release_date = obj['release_date']
                if isinstance(release_date, str):
                    release_date = datetime.strptime(release_date, '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(release_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
            # Parses the cover of the song.
            cover = obj['cover'] if 'cover' in obj else None
            # Parses the jamendo profile of the song.
            jamendo_profile = JamendoSongProfile.from_serialized(
                obj['jamendo_profile']) if 'jamendo_profile' in obj and obj['jamendo_profile'] is not None else None
            # Encapsulate the song.
            song = cls(id=sid, name=name, artist=artist, album=album, cover=cover, duration=duration,
                       release_date=release_date, jamendo_profile=jamendo_profile)
            # Parses the tags of the song.
            if 'tags' in obj and obj['tags']:
                song.tags.add(*[Tag.from_serialized(entry) for entry in obj['tags']])
            return song
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and self.artist == other.artist and self.album == other.album and (
                self.jamendo_id == other.jamendo_id if self.is_on_jamendo and other.is_on_jamendo else True)
        else:
            return False

    def __hash__(self):
        return hash(self.name) ^ hash(self.artist) ^ hash(self.album)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return repr(self)


class SongStatistic(models.Model):
    pass


class JamendoSongStatistic(models.Model):
    pass


class Source(models.Model, SerializableModel):
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
        elif isinstance(obj, dict):
            sid = (int(obj['id']) if 'id' in obj and obj['id'] else None)
            # Parses the type, codec and link of the source.
            type = obj['type'] if 'type' in obj else None
            if type is None and type not in [entry[0] for entry in cls.SOURCE_TYPE]:
                raise DeserializableException('The type \'%s\' of the source is unknown. It must not be None.' % type)
            link = obj['link'] if 'link' in obj else None
            if link is None:
                raise DeserializableException('The link \'%s\' of the source must not be None.' % link)
            codec = obj['codec'] if 'codec' in obj else None
            if codec is None and codec not in [entry[0] for entry in cls.CODEC_TYPE]:
                raise DeserializableException('The codec \'%s\'of the source is unknown. It must not be None.' % codec)
            # Parses the song of the source.
            song = None
            if 'song_id' in obj and obj['song_id']:
                song_query_set = Song.objects.filter(id=int(obj['song_id']))
                song = (song_query_set.first() if song_query_set.exists() else None)
            if song is None:
                raise DeserializableException('The song \'%s\'of the source must not be None.' % str(song))
            return cls(id=sid, type=type, link=link, song=song, codec=codec)
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary (%s).' % (repr(obj), type(obj)))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.type == other.type and self.link == other.link and self.codec == other.codec
        else:
            return False

    def __hash__(self):
        return hash(self.type) ^ hash(self.link) ^ hash(self.codec)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.serialize())

    def __str__(self):
        return '<%s: Type:%s, Link: %s Codec: %s> of %s' % (
            type(self).__name__, self.type, self.link, self.codec, repr(self.song))
