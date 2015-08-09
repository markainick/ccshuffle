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

import logging
import urllib.parse
import requests
from abc import abstractmethod
from .models import Artist, Song, Album, CrawlingProcess

logger = logging.getLogger(__name__)


class Entity(object):
    """ This class represents an entity that is relevant for the search engine. """

    def __init__(self, entity):
        assert entity is not None
        self.entity = entity

    @abstractmethod
    def merge(self, others: []):
        """
        Search for similar entities and tries to merge them, if they may be the same.

        :others: a list of other entities, that are similar to the given entity.
        :return: the current entity or a new merged one.
        """
        pass


class ArtistEntity(Entity):
    """ This class represents the entity artist. """

    def merge(self, others: []):
        pass  # TODO Implement merge

    def artist(self) -> Artist:
        """ Returns the artist. (wrapped in this class) """
        return self.entity


class AlbumEntity(Entity):
    """ This class represents the entity album. """

    def merge(self, others: []):
        pass  # TODO Implement merge

    def album(self) -> Album:
        """ Returns the album. (wrapped in this class) """
        return self.entity


class SongEntity(Entity):
    """ This class represents the entity song. """

    def merge(self, others: []):
        pass  # TODO Implement merge

    def song(self) -> Song:
        return self.entity


class JamendoCallException(Exception):
    """ The exception will be raised, if the jamendo api call has been resulted in an error or unexpected state """

    def __init__(self, message, *args, **kwargs):
        super(JamendoCallException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message


class JamendoServiceMixin(object):
    """ The jamendo service mixin provides the utilities to communicate with the jamendo web service (REST Api). """

    client_id = '0a7472b2'
    api_url = 'https://api.jamendo.com/v3.0/'

    @classmethod
    def json_call(cls, qualifier, properties={}, hooks={}):
        """
        Sends a request with the given qualifier and properties to the jamendo webservice and returns the response.
        A JamendoCallException will be raised, if the response is corrupted or the api call was not successful.

        :param qualifier: the qualifier indicates the required command of the rest api (f.e. artist).
        :param properties: a dictionary with the  optional properties of the command.
        :param hooks: event hooks that shall be used for the request.
        :return: the response of the jamendo api, if the call was successful. Otherwise an exception will be raised.
        """
        properties['client_id'] = cls.client_id
        properties['format'] = 'json'
        request_url = cls.api_url + '%s/?%s' % (qualifier, urllib.parse.urlencode(properties))
        print('Request[%s]: %s' % (qualifier, request_url))
        logger.debug('Request[%s]: %s' % (qualifier, request_url))
        response = requests.get(request_url, hooks=hooks).json()
        if response is None or not ('headers' in response and 'results' in response):
            raise JamendoCallException('The response of the jamendo api call is corrupted !')
        elif response['headers']['status'] != 'success':
            raise JamendoCallException('The jamendo api call failed (%s)!' % response['headers']['error_message'])
        return response

    @classmethod
    def all_query(cls, qualifier, properties={}, process=None):
        """
        This method is a template for getting all data sets for a special entity. The function 'call' must be given.
        This function is called unless the response of the function is empty.

        :param qualifier: the required qualifier, which shall be used for the json call (f.e. songs, tracks, albums).
        :param properties: optional properties, which shall be used for the json call. The properties 'limit' as well as
                           offset will be overwritten.
        :param process: an optional function that takes a list of json dictionaries (jamendo entities) as argument
                        and returns a list. This list will be used for the further processing.
        """
        offset = 0
        result_list = []
        properties['limit'] = 'all'
        while True:
            properties['offset'] = offset
            response = cls.json_call(qualifier, properties=properties)
            if response['headers']['results_count'] == 0 or not response['results']:
                break
            else:
                offset += int(response['headers']['results_count'])
                new_entities_list = response['results']
                if process is not None:
                    new_entities_list = process(new_entities_list)
                result_list.extend(new_entities_list)
        return result_list


class JamendoArtistEntity(ArtistEntity, JamendoServiceMixin):
    """ This class represents the entity artist of the jamendo service. """

    def __init__(self, jamendo_artist: {str: str}):
        super(JamendoArtistEntity, self).__init__(self.__parse_json(jamendo_artist))

    @classmethod
    def get_or_create(cls, name: str=None, jamendo_id: str=None) -> Artist:
        """
        Returns the artist with the given properties.

        :param name: the name of the artist, which shall be returned.
        :param jamendo_id: the jamendo id of the artist, which shall be returned.
        :return: one artist or None.
        """
        if jamendo_id is not None:
            response_set = Artist.objects.filter(jamendo_id=jamendo_id)
            if response_set.exists():
                return response_set.first()
            else:
                response = cls.json_call('artists', {'id': jamendo_id})
                if response['headers']['results_count'] == 1:
                    artist = JamendoArtistEntity(response['results'][0]).artist()
                    artist.save()
                    return artist
                else:
                    pass  # Todo Implement super.get()
        elif name is not None:
            pass  # TODO Implement super.get()
        else:
            raise ValueError('The name or the jamendo id must be given !')

    @classmethod
    def all_artists(cls) -> [Artist]:
        """
        This method scans for all artists available on the jamendo service and persists them if the artist has not
        been already persisted.

        :param artists_list: the list of already loaded or known artists.
        :return: the loaded artists with no duplicates regarding the jamendo_id.
        """

        def process_result(artists_json):
            artists = [JamendoArtistEntity(artist).artist() for artist in artists_json]
            Artist.objects.bulk_create(artists)
            return artists

        logger.info('SE (Jamendo): Crawling for all artists !')
        return cls.all_query('artists', process=process_result)

    @classmethod
    def __parse_json(cls, jamendo_artist: {str: str}) -> Artist:
        """
        Parses the given information about an artist (retrieved from jamendo - formatted as json) into an artist model.

        :param jamendo_artist: the artist information, which has been retrieved from jamendo formatted as json.
        :return: the artist model.
        """
        artist = Artist()
        artist.name = jamendo_artist['name']
        artist.jamendo_id = jamendo_artist['id']
        artist.abstract = ''
        artist.website = jamendo_artist['website']
        artist.country_code = ''
        artist.city = ''
        return artist


class JamendoAlbumEntity(AlbumEntity, JamendoServiceMixin):
    """ This class represents the entity artist of the jamendo service. """

    def __init__(self, jamendo_album: {str: str}):
        super(JamendoAlbumEntity, self).__init__(self.__parse_json(jamendo_album))

    @classmethod
    def get_or_create(cls, name: str=None, jamendo_id: str=None) -> Artist:
        """
        Returns the album with the given properties.

        :param name: the name of the album, which shall be returned.
        :param jamendo_id: the jamendo id of the album, which shall be returned.
        :return: one album or None.
        """
        if jamendo_id is not None:
            response_set = Album.objects.filter(jamendo_id=jamendo_id)
            if response_set.exists():
                return response_set.first()
            else:
                response = cls.json_call('albums', {'id': jamendo_id})
                if response['headers']['results_count'] == 1:
                    album = JamendoAlbumEntity(response['results'][0]).album()
                    album.save()
                    return album
                else:
                    pass  # Todo Implement super.get()
        elif name is not None:
            pass  # TODO Implement super.get()
        else:
            raise ValueError('The name or the jamendo id must be given !')

    @classmethod
    def all_albums(cls) -> [Album]:
        """
        This method scans for all albums available on the jamendo service and persists them if the album has not
        been already persisted.

        :return: the loaded albums with no duplicates regarding the jamendo_id.
        """

        def process_result(albums_json):
            albums = [JamendoAlbumEntity(album).album() for album in albums_json]
            Album.objects.bulk_create(albums)
            return albums

        logger.info('SE (Jamendo): Crawling for all albums !')
        return cls.all_query('albums', process=process_result)

    @classmethod
    def __parse_json(cls, jamendo_album: {str: str}) -> Album:
        """
        Parses the given information about an album (retrieved from jamendo - formatted as json) into an album model.

        :param album_json: the album information, which has been retrieved from jamendo formatted as json.
        :return: the album model.
        """
        album = Album()
        album.jamendo_id = jamendo_album['id']
        album.name = jamendo_album['name']
        album.artist = JamendoArtistEntity.get_or_create(jamendo_id=jamendo_album['artist_id'],
                                                         name=jamendo_album['artist_name'])
        album.release_date = jamendo_album['releasedate']
        return album


class JamendoSongEntity(SongEntity, JamendoServiceMixin):
    """ This class represents the entity song of the jamendo service. """

    def __init__(self, jamendo_song: {str: str}):
        super(JamendoSongEntity, self).__init__(self.__parse_json(jamendo_song))

    @classmethod
    def all_songs(cls) -> [Song]:
        """
        This method scans for all songs available on the jamendo service and persists them if the song has not
        been already persisted.

        :return: the loaded songs with no duplicates regarding the jamendo_id.
        """

        def process_result(songs_json):
            songs = [JamendoSongEntity(song).song() for song in songs_json]
            Song.objects.bulk_create(songs)
            return songs

        logger.info('SE (Jamendo): Crawling for all songs !')
        return cls.all_query('tracks', process=process_result)

    @classmethod
    def __parse_json(cls, jamendo_song: {str: str}) -> Song:
        """
        Parses the given information about a song (retrieved from jamendo - formatted as json) into an song model.

        :param: the song information, which has been retrieved from jamendo formatted as json.
        :return: the song model.
        """
        song = Song()
        song.jamendo_id = jamendo_song['id']
        song.name = jamendo_song['name']
        song.duration = int(jamendo_song['duration'])
        song.release_date = jamendo_song['releasedate']
        song.album = JamendoAlbumEntity.get_or_create(name=jamendo_song['album_name'],
                                                      jamendo_id=jamendo_song['album_id'])
        song.artist = JamendoArtistEntity.get_or_create(name=jamendo_song['artist_name'],
                                                        jamendo_id=jamendo_song['artist_id'])
        return song


class JamendoSearchEngine(object):
    """ This class scans for creative commons music from the Jamendo webservice <https://www.jamendo.com>. """

    @classmethod
    def crawl(cls) -> None:
        """ Starts a new crawling process """
        crawling_process = CrawlingProcess(service=CrawlingProcess.Service_Jamendo,
                                           status=CrawlingProcess.Status_Running)
        crawling_process.save()
        try:
            cls.__crawl()
            crawling_process.status = CrawlingProcess.Status_Finished
        except Exception as e:
            logger.exception(e)
            crawling_process.status = CrawlingProcess.Status_Failed
            crawling_process.exception = e.__str__()
        finally:
            crawling_process.save()

    @classmethod
    def __crawl(cls) -> None:
        """ Performs the crawling process. """
        JamendoArtistEntity.all_artists()
        JamendoAlbumEntity.all_albums()
        JamendoSongEntity.all_songs()
