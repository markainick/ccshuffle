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
import json
import sys
import urllib
import requests
from datetime import datetime
from django.test import TestCase
from django.utils.unittest import skip
from ccshuffle.serialize import JSONModelEncoder
from shuffle.models import Song, Artist, Album, Source, License
from .crawler import (JamendoCrawler, JamendoCallException, JamendoServiceMixin, JamendoArtistEntity, JamendoSongEntity,
                      JamendoAlbumEntity)
from .models import CrawlingProcess


class ModelTest(TestCase):
    """ Tests the models of the crawler app """

    def test_serializable_crawling_process(self):
        """ Tests if the model crawling process is serializable """
        crawling_process = CrawlingProcess(service=CrawlingProcess.Service_Jamendo,
                                           execution_date=datetime(year=1979, month=10, day=30),
                                           status=CrawlingProcess.Status_Failed, exception='This is a exception.')
        crawling_process_serialized = crawling_process.serialize()
        crawling_process_des = crawling_process.from_serialized(crawling_process_serialized)
        self.assertEqual(crawling_process_des.service, crawling_process.service,
                         'The information about the service shall not be lost.')
        self.assertEqual(crawling_process_des.status, crawling_process.status,
                         'The information about the status shall not be lost.')
        self.assertEqual(crawling_process_des.execution_date, crawling_process.execution_date,
                         'The information about the execution date shall not be lost.')
        self.assertEqual(crawling_process_des.exception, crawling_process.exception,
                         'The information about the exception shall not be lost.')

    def test_json_encoding_crawling_process(self):
        """ Tests if the model crawling process can be converted to JSON """
        crawling_process = CrawlingProcess(service=CrawlingProcess.Service_Jamendo,
                                           execution_date=datetime(year=1979, month=10, day=30),
                                           status=CrawlingProcess.Status_Failed, exception='This is a exception.')
        crawling_process_json = json.dumps(crawling_process, cls=JSONModelEncoder)
        crawling_process_load = json.loads(crawling_process_json)
        self.assertEqual(crawling_process_load['service'], crawling_process.service,
                         'The information about the service shall not be lost.')
        self.assertEqual(crawling_process_load['status'], crawling_process.status,
                         'The information about the status shall not be lost.')
        self.assertEqual(datetime.strptime(crawling_process_load['execution_date'], '%Y-%m-%dT%H:%M:%S'),
                         crawling_process.execution_date, 'The information about the execution date shall not be lost.')
        self.assertEqual(crawling_process_load['exception'], crawling_process.exception,
                         'The information about the exception shall not be lost.')


class JamendoCrawlerTest(TestCase):
    def __check_connection(self):
        """ Tests if the the jamendo service answers to requests. """
        properties = {
            'client_id': JamendoServiceMixin.client_id,
            'id': 1247375,
            'format': 'json',
        }
        response = requests.get(
            '%stracks/?%s' % (JamendoServiceMixin.api_url, urllib.parse.urlencode(properties))).json()
        if 'headers' in response and response['headers']['status'] == 'success':
            return True
        else:
            if 'headers' in response and 'error_message' in response['headers']:
                print(response['headers']['error_message'], file=sys.stderr)
            return False

    def test_artist_merge_jamendo_songs(self):
        """
        Tests, if the merge of an already existing jamendo song and the received song with the same id is successful.

        The test songs are 'Possibilities' from Jasmine Jordan and 'War' of Waterpistols.
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
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

    def test_song_license(self):
        """
        Tests if the license of the fetched songs are persisted correctly.

        The test songs are:
             'Melody for the grass' from Waterpistols > License: CC-BY-NC-SA.
             'I Don't Know What I'm Doing' from Brad Sucks > License: CC-BY-NC-SA.
             'Celebrate' from Devinjai > License: CC-BY-ND
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        song_melody_for_the_grass = JamendoSongEntity.get_or_create(jamendo_id=30058)
        self.assertEqual(song_melody_for_the_grass.license.type, License.CC_BY_NC_SA,
                         'The license of the song \'Melody for the grass\' must be CC-BY-NC-SA')
        song_i_dont_know_what_im_doing = JamendoSongEntity.get_or_create(jamendo_id=1241183)
        self.assertEqual(song_i_dont_know_what_im_doing.license.type, License.CC_BY_NC_SA,
                         'The license of the song \'I Don\'t Know What I\'m Doing\' must be CC-BY-NC-SA')
        song_celebrate = JamendoSongEntity.get_or_create(jamendo_id=1233793)
        self.assertEqual(song_celebrate.license.type, License.CC_BY_ND,
                         'The license of the song \'Celebrate\' must be CC-BY-ND')

    def test_song_source(self):
        """
        Tests if the sources receveived from jamendo for the song are persisted correctly and can be accessed by the
        source method.

        The test song is 'Possibilities' from Jasmine Jordan.
            Audio stream link: https://storage.jamendo.com/?trackid=1230403&format=mp31
            Download link: https://storage.jamendo.com/download/track/1230403/mp32/
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        song_jasmine_possibilities = JamendoSongEntity.get_or_create(jamendo_id=1230403)
        self.assertEqual(len(song_jasmine_possibilities.sources(type=Source.TYPE_STREAM, codec=Source.CODEC_MP3)), 1,
                         'There must be one streaming link persisted for this song (Codec: MP3).')
        self.assertIn('https://storage.jamendo.com/?trackid=1230403&format=mp31',
                      song_jasmine_possibilities.sources(type=Source.TYPE_STREAM, codec=Source.CODEC_MP3)[0].link,
                      'The link for streaming the audio (codec: MP3) must be persisted.')
        self.assertEqual(len(song_jasmine_possibilities.sources(type=Source.TYPE_DOWNLOAD, codec=Source.CODEC_MP3)), 1,
                         'There must be one download link persisted for this song (Codec: MP3).')
        self.assertIn('https://storage.jamendo.com/download/track/1230403/mp32/',
                      song_jasmine_possibilities.sources(type=Source.TYPE_DOWNLOAD, codec=Source.CODEC_MP3)[0].link,
                      'The link for downloading the audio track (codec: MP3) must be persisted.')

    def test_song_tags(self):
        """
        Tests if the received tags of the songs are persisted correctly and connected to the song.
        The sample data contains the song with the jamendo id

        The song 'Possibilities' of Jasmine Jordan is used for testing.
        """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        song_jasmine_possibilities = JamendoSongEntity.get_or_create(jamendo_id=1230403)
        song_jasmine_pos_tags = [tag.name for tag in song_jasmine_possibilities.tags.all()]
        song_jasmine_pos_tags.sort()
        tags = ['pop', '90s', 'rnb', 'groove', 'dream', 'happy', 'peaceful', 'electric', 'soulfull']
        tags.sort()
        self.assertListEqual(song_jasmine_pos_tags, tags,
                             'The linked tags of the song \'Possibilities\' of Jasmine must be equal to the given list.')

    @skip('Long runtime')
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

    @skip('Long runtime')
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

    @skip('Long runtime')
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

    @skip('Long runtime')
    def test_crawl(self):
        """ Tests the crawling process """
        self.assertTrue(self.__check_connection(), 'The jamendo webservice must be reachable.')
        JamendoCrawler.crawl()
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
        JamendoCrawler.crawl()
        JamendoServiceMixin.client_id = client_id
        # Check if the crawling process was logged into the database.
        p = CrawlingProcess.objects.all().last()
        self.assertEqual('Jamendo', p.service, 'The last crawling process must be a jamendo job.')
        self.assertEqual('Failed', p.status, 'The last crawling must have been failed.')
        self.assertIn('Your credential is not authorized.', p.exception,
                      'The exception message must contain \' Your credential is not authorized. \'')
