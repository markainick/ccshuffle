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
from .models import Artist, Song, Album

logger = logging.getLogger(__name__)


class JamendoJsonParser(object):
    """
    This class provides methods to parse the required entities retrieved from jamendo into the corresponding models
    of the ccshuffle service.
    """

    @staticmethod
    def parse_song(song_json):
        """
        Parses the given information about an song (retrieved from jamendo - formatted as json) into an song model.

        :param: the song information, which has been retrieved from jamendo formatted as json.
        :return: the song model.
        """
        song = Song()
        song.id = song_json['id']
        song.name = song_json['name']
        song.duration = int(song_json['duration'])
        song.release_date = song_json['releasedate']
        song.album = None
        return song

    @staticmethod
    def parse_artist(artist_json):
        """
        Parses the given information about an artist (retrieved from jamendo - formatted as json) into an artist model.

        :param artist_json: the artist information, which has been retrieved from jamendo formatted as json.
        :return: the artist model.
        """
        artist = Artist()
        artist.name = artist_json['name']
        artist.jamendo_id = artist_json['id']
        artist.abstract = ''
        artist.website = artist_json['website']
        artist.country_code = ''
        artist.city = ''
        return artist


class JamendoEngine(object):
    """
    This class scans for creative commons music from the Jamendo webservice <https://www.jamendo.com>. The REST API
    of Jamendo is used to do this <https://developer.jamendo.com/v3.0/>.
    """
    client_id = '0a7472b2'
    api_url = 'https://api.jamendo.com/v3.0/'

    def crawl(self):
        pass

    def all_songs(self):
        """
        This method scans for all songs available on the jamendo service and persists them if the song has not
        been already persisted.

        :return: the loaded songs with no duplicates regarding the jamendo_id.
        """
        logger.debug('Crawling for all jamendo songs.')
        offset = 0
        new_songs_list = []
        while True:
            response = self._all_songs_query(offset)
            logger.debug('Response[Song]: %s' % response)
            if 'headers' not in response or response['headers']['status'] != 'success':
                logger.exception('The response of the song query is corrupted !')
                raise JamendoCrawlerEngineException('The response of the song query is corrupted !')
            elif response['headers']['results_count'] == 0 or not response['results']:
                break
            else:
                offset += int(response['headers']['results_count'])
                new_songs = [song for song in
                             [JamendoJsonParser.parse_song(song_entry) for song_entry in response['results']] if
                             not Song.objects.filter(jamendo_id=song.jamendo_id).exists()]
                new_songs_list.extend(new_songs)
        # TODO Merge with other song (if necessary)
        Song.objects.bulk_create(new_songs_list)
        return new_songs_list

    def _all_songs_query(self, offset=0):
        """
        This method scans for all songs available on the jamendo service and persists them if the song has not
        been already persisted.

        :param offset: the number of songs, which shall be skipped.
        :return: the response of the jamendo service as json.
        """
        properties = {
            'client_id': self.client_id,
            'format': 'json',
            'limit': 'all',
            'offset': offset
        }
        return requests.get(self.api_url + 'tracks/?%s' % urllib.parse.urlencode(properties)).json()

    def artist(self, jamendo_id=None, name=None):
        """
        This method searches for the artist with the given properties. Either the jamendo_id or the name must be set
        (must not be None).

        :param jamendo_id: the jamendo id of the artist.
        :param name: the name of the artist.
        :return: the artist or None if no artist with this properties can be found.
        """
        if (jamendo_id is not None) and (name is not None):
            raise ValueError('Either the jamendo id or the name must be given.')
        artist_list = Artist.objects.filter(jamendo_id=jamendo_id, name=name)
        if artist_list is None or not artist_list:
            response = self.__artist_query(jid=jamendo_id, name=name)
            logger.debug('Response[Artist]: %s' % response)
            if not response['results']:
                return None
            elif len(response['results']) == 1:
                artist = JamendoJsonParser.parse_artist(response['results'][0])
                # TODO Merge artists, persist artist.
                return artist
            else:
                return JamendoJsonParser.parse_artist(response['results'][0])  # TODO What artist shall be used ?
        else:
            return artist_list[0]  # TODO What artist shall be used ?

    def all_artists(self, artists_list=None):
        """
        This method scans for all artists available on the jamendo service and persists them if the artist has not
        been already persisted.

        :param artists_list: the list of already loaded or known artists.
        :return: the loaded artists with no duplicates regarding the jamendo_id.
        """
        logger.debug('Crawling for jamendo artists.')
        offset = 0
        new_artists_list = []
        while True:
            response = self.__all_artists_query(offset)
            logger.debug('Response[Artists]: %s' % response)
            if 'headers' not in response or response['headers']['status'] != 'success':
                logger.exception('The response of the artist query is corrupted !')
                raise JamendoCrawlerEngineException('The response of the artist query is corrupted !')
            elif response['headers']['results_count'] == 0 or not response['results']:
                break
            else:
                offset += int(response['headers']['results_count'])
                new_artists = [artist for artist in
                               [JamendoJsonParser.parse_artist(artist_entry) for artist_entry in response['results']]
                               if not Artist.objects.filter(jamendo_id=artist.jamendo_id)]
                new_artists_list.extend(new_artists)
        # TODO Merge with other artist (if necessary)
        Artist.objects.bulk_create(new_artists_list)
        return new_artists_list

    def __get_or_merge_artist(self):
        pass

    def __artist_query(self, jid=None, name=None, limit='all', offset=0):
        """
        This method tries to fetch the artist with the given properties.

        :param jid: the jamendo id of the artist
        :param name: the name of the artist
        :param limit: the limit of artists to fetch. The maximal number is 200.
        :param offset: the number of artists, who shall be skipped.
        :return: the response of the jamendo service as json.
        """
        properties = {
            'client_id': self.client_id,
            'format': 'json',
            'limit': limit,
            'offset': offset
        }
        if jid is not None:
            properties['id'] = jid
        if name is not None:
            properties['name'] = name
        return requests.get(self.api_url + 'artists/?%s' % urllib.parse.urlencode(properties)).json()

    def __all_artists_query(self, offset=0):
        """
        This method tries to fetch 'all' artist. The 'all' is limited to 200 entries. To fetch all artists this
        method may be executed further times using the offset parameter.

        :param offset: the number of artists, which shall be skipped.
        :return: the response of the jamendo service as json.
        """
        properties = {
            'client_id': self.client_id,
            'format': 'json',
            'limit': 'all',
            'offset': offset
        }
        return requests.get(self.api_url + 'artists/?%s' % urllib.parse.urlencode(properties)).json()


class JamendoCrawlerEngineException(Exception):
    """ This class represents an exception, which will be thrown, if the crawling of the Jamendo webservice fails. """

    def __init__(self, message, *args, **kwargs):
        super(JamendoCrawlerEngineException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message
