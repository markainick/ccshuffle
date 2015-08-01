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
from .searchengine import JamendoEngine
from .models import Artist, Song
import logging

logger = logging.getLogger(__name__)


class HomePageViewTest(TestCase):
    client = Client()


class JamendoEngineTest(TestCase):
    """ Unittests for the jamendo crawler. """
    jamendo_crawler_engine = JamendoEngine()

    def __check_connection(self):
        return True

    def test_all_songs(self):
        """
        Tests the functionality to load all songs, which are stored on jamendo.

        Checks if the following songs are fetched (spot check): 8BIT FAIRY TALE, Bohemia, Melody for the grass,
                                                                GO!GO!GO!, Skibidubap
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        self.jamendo_crawler_engine.all_songs()
        for song in ('8BIT FAIRY TALE', 'Bohemia', 'Melody for the grass', 'GO!GO!GO!', 'Skibidubap'):
            self.assertTrue(Song.objects.filter(name=song).exists(),
                            '\'%s\' must be in the database after scanning jamendo for songs' % song)

    def test_artist_new_jamendo_id(self):
        """
        Tests the functionality, if the artist given to the method is currently not persisted (unknown), but can be
        found on the jamendo webservice. The jamendo id is given to identify the artist.
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        artist = self.jamendo_crawler_engine.artist(jamendo_id=471621)
        self.assertIsNotNone(artist, 'The artist \'Jasmine Jordan\' must be found.')
        self.assertEqual('Jasmine Jordan', artist.name, 'The name of the found artist must be \'Jasmine Jordan\'.')

    def test_artist_new_name(self):
        """
        Tests the functionality, if the artist given to the method is currently not persisted (unknown), but can be
        found on the jamendo webservice. The name is given to identify the artist.
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        artist = self.jamendo_crawler_engine.artist(name='Jasmine Jordan')
        self.assertIsNotNone(artist, 'The artist \'Jasmine Jordan\' must be found.')
        self.assertEqual(471621, int(artist.jamendo_id), 'The id of the found artist must be \'471621\'.')

    def test_all_artists(self):
        """
        Tests the functionality to load all artists, which are stored on jamendo.

        Checks if the following artists are fetched (spot check): Jasmine Jordan, LukHash, Terrible Terrible, Bellevue
        """
        self.assertTrue(self.__check_connection(), "The jamendo webservice must be reachable.")
        self.jamendo_crawler_engine.all_artists()
        for artist_name in ('Jasmine Jordan', 'LukHash', 'Terrible Terrible', 'Bellevue'):
            self.assertTrue(Artist.objects.filter(name=artist_name).exists(),
                            "'%s' must be in the database after scanning jamendo for artists" % artist_name)
