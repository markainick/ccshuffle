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
from .searchengine import JamendoSearchEngine, JamendoCallException, JamendoServiceMixin
from .searchengine import JamendoArtistEntity, JamendoSongEntity, JamendoAlbumEntity
from .models import Artist, Song, Album, CrawlingProcess
import logging

logger = logging.getLogger(__name__)


class HomePageViewTest(TestCase):
    client = Client()


class JamendoEngineTest(TestCase):
    """ Unittests for the jamendo crawler. """

    def __check_connection(self):
        return True

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
