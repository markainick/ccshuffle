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

from django.test import TestCase, Client
from django.utils import unittest
from datetime import datetime
from .searchengine import JamendoSearchEngine, JamendoCallException, JamendoServiceMixin
from .searchengine import JamendoArtistEntity, JamendoSongEntity, JamendoAlbumEntity
from .models import JSONModelEncoder, Artist, Song, Album, CrawlingProcess
from .views import ResponseObject
import logging

logger = logging.getLogger(__name__)

import json


class HomePageViewTest(TestCase):
    client = Client()


class CrawlingDashboardTest(unittest.TestCase):
    """ Unittests for the jamendo crawling dashboard. """

    def test_crawling_process_json(self):
        """ Tests if the crawling process class can be serialized with json."""
        crawling_process = CrawlingProcess(service=CrawlingProcess.Service_Jamendo, execution_date=datetime.now(),
                                           status=CrawlingProcess.Status_Failed)
        response_object = ResponseObject(result_obj=crawling_process)
        json_result = response_object.json(cls=JSONModelEncoder)
        json_result = json.loads(json_result)
        self.assertEqual(json_result['result']['status'], 'Failed',
                         'The info about the crawling process shall not be lost!')
        self.assertEqual(json_result['result']['service'], CrawlingProcess.Service_Jamendo,
                         'The info about the crawling process shall not be lost!')
        self.assertEqual(json_result['header']['status'], 'success', 'The header shall contain the status information')


class JamendoEngineTest(TestCase):
    """ Unittests for the jamendo crawler. """

    def __check_connection(self):
        return True

    def test_artist_merge_jamendo_songs(self):
        """
        Tests, if the merge of an already existing jamendo song and the received song with the same id is successful.

        The test songs are 'Possibilities' from Jasmine Jordan and 'War' of Waterpistols.
        """
        # Jasmin Jordan - Possibilities
        song_jasmine_possibilities = JamendoSongEntity.get_or_create(jamendo_id=1230403)
        db_id = song_jasmine_possibilities.id
        # Test the merge for this song.
        song_jasmine_possibilities = JamendoSongEntity.get_or_create(jamendo_id=1230403)
        self.assertEqual(song_jasmine_possibilities.id, db_id, 'The id must stay the same.')
        # Waterpistol - War
        song_waterpistol_war = JamendoSongEntity.get_or_create(jamendo_id=1241182)
        db_id = song_waterpistol_war.id
        # Test the merge for this song.
        song_waterpistol_war = JamendoSongEntity.get_or_create(jamendo_id=1241182)
        self.assertEqual(song_waterpistol_war.id, db_id, 'The id must stay the same.')

    def test_song_tags(self):
        """
        Tests if the transmitted tags of the songs are persisted and connected correctly to the song.
        The sample data contains the song with the jamendo id

        The song 'Possibilities' of Jasmine Jordan is used for testing.
        """
        song_jasmine_possibilities = JamendoSongEntity.get_or_create(jamendo_id=1230403)
        song_jasmine_pos_tabs = [tag.name for tag in song_jasmine_possibilities.tags.all()]
        song_jasmine_pos_tabs.sort()
        self.assertEqual(len(song_jasmine_pos_tabs), 7, 'There must be 7 tags linked to the song \'Possibilities\'.');
        self.assertListEqual(song_jasmine_pos_tabs,
                             ['electric', 'funk', 'groove', 'happy', 'pop', 'rnb', 'soulfull'],
                             'The linked tags of the song \'Possibilities\' of Jasmine must be equal to the given list.')

    @unittest.skip('Long runtime')
    def test_all_songs(self):
        """
        Tests the functionality to load all songs, which are stored on jamendo.

        Checks if the following songs are fetched (spot check): 8BIT FAIRY TALE, Bohemia, Melody for the grass,
                                                                GO!GO!GO!, Skibidubap
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        JamendoSongEntity.all_songs()
        for song in ('8BIT FAIRY TALE', 'Bohemia', 'Melody for the grass', 'GO!GO!GO!', 'Skibidubap'):
            self.assertTrue(Song.objects.filter(name=song).exists(),
                            '\'%s\' must be in the database after scanning jamendo for songs' % song)

    @unittest.skip('Long runtime')
    def test_all_albums(self):
        """
        Tests the functionality to load all albums, which are stored on jamendo.

        Checks if the following albums are fetched (spot check): Blue Waters EP, Connection, After, 8-bit lagerfeuer
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        JamendoAlbumEntity.all_albums()
        for album in ('Blue Waters EP', 'Connection', 'After', '8-bit lagerfeuer'):
            self.assertTrue(Album.objects.filter(name=album).exists(),
                            '\'%s\' must be in the database after scanning jamendo for albums' % album)

    @unittest.skip('Long runtime')
    def test_all_artists(self):
        """
        Tests the functionality to load all artists, which are stored on jamendo.

        Checks if the following artists are fetched (spot check): Jasmine Jordan, LukHash, Terrible Terrible, Bellevue
        """
        self.assertTrue(self.__check_connection(), "The jamendo webservice must be reachable.")
        JamendoArtistEntity.all_artists()
        for artist_name in ('Jasmine Jordan', 'LukHash', 'Terrible Terrible', 'Bellevue'):
            self.assertTrue(Artist.objects.filter(name=artist_name).exists(),
                            "'%s' must be in the database after scanning jamendo for artists" % artist_name)

    def test_all_artists_wrong_client_id(self):
        """ Tests the behaviour if the jamendo api call is not successful. """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        client_id = JamendoServiceMixin.client_id
        JamendoServiceMixin.client_id = '#####'
        self.assertRaises(JamendoCallException, JamendoArtistEntity.all_artists)
        JamendoServiceMixin.client_id = client_id

    @unittest.skip('Long runtime')
    def test_crawl(self):
        """ Tests the crawling process """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        JamendoSearchEngine.crawl()
        # Song with the name 'Possibilities' must exist.
        possibilities_songs = Song.objects.filter(name='Possibilities')
        self.assertTrue(possibilities_songs.exists(), 'The song \'Possibilities\' of Jasmin Jordan must exist.')
        self.assertIn('Jasmine Jordan', [song.artist.name for song in possibilities_songs if song.artist is not None])
        self.assertIn('Time Travel EP', [song.album.name for song in possibilities_songs if song.album is not None])
        # Song with the name 'Kick Drum'n Bass' must exist
        kick_dnb_songs = Song.objects.filter(name='Kick Drum\'n Bass')
        self.assertTrue(kick_dnb_songs.exists(), 'The song \'Possibilities\' of Jasmin Jordan must exist.')
        self.assertIn('Kick Drum\'n Bass', [song.artist.name for song in kick_dnb_songs if song.artist is not None])
        self.assertIn('Trip\'N\'Bass', [song.album.name for song in kick_dnb_songs if song.album is not None])

    def test_crawl_fails(self):
        """ Tests the behaviour, if the crawling fails. """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        client_id = JamendoServiceMixin.client_id
        JamendoServiceMixin.client_id = '#####'
        JamendoSearchEngine.crawl()
        JamendoServiceMixin.client_id = client_id
        # Check if the crawling process was logged into the database.
        p = CrawlingProcess.objects.all().last()
        self.assertEqual('Jamendo', p.service, 'The last crawling process must be a jamendo job.')
        self.assertEqual('Failed', p.status, 'The last crawling must have been failed.')
        self.assertIn('Your credential is not authorized.', p.exception,
                      'The exception message must contain \' Your credential is not authorized. \'')
