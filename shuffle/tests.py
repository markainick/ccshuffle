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

from django.test import TestCase, Client, TransactionTestCase
from django.utils.unittest import skip
from datetime import datetime
from .searchengine import JamendoSearchEngine, JamendoCallException, JamendoServiceMixin
from .searchengine import JamendoArtistEntity, JamendoSongEntity, JamendoAlbumEntity
from .models import JSONModelEncoder, Artist, Song, Album, Tag, CrawlingProcess
from .views import ResponseObject

import json
import logging

logger = logging.getLogger(__name__)


class HomePageViewTest(TestCase):
    client = Client()


class CrawlingDashboardTest(TestCase):
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


class ModelTest(TestCase):
    """ Test the model classes. """

    def test_eq_hash_tag(self):
        """
        Tests if tags with the same name are equal (must have also the same hash value) and tags with different
        names not.
        """
        tag_indie_rock_1 = Tag(name='indie rock')
        tag_indie_rock_2 = Tag(name='indie rock')
        self.assertEqual(tag_indie_rock_1, tag_indie_rock_2, 'Tags with the same name must be equal.')
        tag_pop = Tag(name='pop')
        self.assertNotEqual(tag_indie_rock_1, tag_pop, 'Tags with different names must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(tag_indie_rock_1), hash(tag_indie_rock_2),
                         'The has value of tags with the same name must be equal.')

    def test_eq_hash_artists(self):
        """
        Tests if artists with the same name (and service ids) are equal and artists with different names or different
        ids.
        """
        artist_beatles_1 = Artist(name='The Beatles')
        artist_beatles_2 = Artist(name='The Beatles')
        self.assertEqual(artist_beatles_1, artist_beatles_2, 'Artists with the same name must be equal.')
        artist_pink_floyd_1 = Artist(name='Pink Floyd', jamendo_id=1)
        self.assertNotEqual(artist_pink_floyd_1, artist_beatles_1,
                            'Artists with the different names must not be equal.')
        artist_pink_floyd_2 = Artist(name='Pink Floyd', jamendo_id=1)
        self.assertEqual(artist_pink_floyd_1, artist_pink_floyd_2,
                         'Artists with the same name and service id must be equal.')
        artist_pink_floyd_2 = Artist(name='Pink Floyd', jamendo_id=2)
        self.assertNotEqual(artist_pink_floyd_1, artist_pink_floyd_2,
                            'If the jamendo id differs, the artists must not be equal (also if they have the same)')
        # Tests the hashing.
        self.assertEqual(hash(artist_beatles_1), hash(artist_beatles_2), 'The hash of two equal artists must be equal.')

    def test_eq_hash_albums(self):
        """ Tests if albums with the same name and same artist (as well as service id) are equal. """
        artist_beatles = Artist(name='The Beatles')
        artist_beatles.save()
        artist_pink_floyd = Artist(name='Pink Floyd')
        artist_pink_floyd.save()
        album_abbey_road_1 = Album(name='Abbey Road', artist=artist_beatles)
        album_abbey_road_2 = Album(name='Abbey Road', artist=artist_beatles, jamendo_id=1)
        self.assertEqual(album_abbey_road_1, album_abbey_road_2, 'Albums with the same name and artist must be equal.')
        album_abbey_road_3 = Album(name='Abbey Road', artist=artist_pink_floyd)
        self.assertNotEqual(album_abbey_road_1, album_abbey_road_3,
                            'If the artist differs, the albums must not be equal.')
        album_the_wall_1 = Album(name='The Wall', artist=artist_pink_floyd, jamendo_id=3)
        album_the_wall_2 = Album(name='The Wall', artist=artist_pink_floyd, jamendo_id=3)
        self.assertEqual(album_the_wall_1, album_the_wall_2,
                         'If the name and service ids of the albums are the same, they must be equal.')
        album_the_wall_3 = Album(name='The Wall', artist=artist_pink_floyd, jamendo_id=4)
        self.assertNotEqual(album_the_wall_1, album_the_wall_3,
                            'If one of the service id differs, the albums must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(album_abbey_road_1), hash(album_abbey_road_2),
                         'The hash of two equal albums must be equal.')

    def test_eq_hash_songs(self):
        """Tests if songs with the same name, album and artist must be equal (must have also the same hash value). """
        # Artists
        artist_beatles = Artist(name='The Beatles')
        artist_beatles.save()
        artist_pink_floyd = Artist(name='Pink Floyd')
        artist_pink_floyd.save()
        artist_gorillaz = Artist(name='Gorillaz')
        artist_gorillaz.save()
        # Album
        album_abbey_road = Album(name='Abbey Road', artist=artist_beatles).save()
        album_the_wall = Album(name='The Wall', artist=artist_pink_floyd, jamendo_id=3).save()
        # Test the equal method.
        song_another_brick_1 = Song(name='Another brick in the wall', artist=artist_pink_floyd, album=album_the_wall,
                                    jamendo_id=1)
        song_another_brick_2 = Song(name='Another brick in the wall', artist=artist_pink_floyd, album=album_the_wall)
        self.assertEqual(song_another_brick_1, song_another_brick_2,
                         'The song with same name, artist and album must be equal.')
        song_clint_eastwood = Song(name='Clint Eastwood (Single)', artist=artist_gorillaz, jamendo_id=2)
        self.assertEqual(song_clint_eastwood, song_clint_eastwood,
                         'Singles with the same name and artist must be the same.')
        self.assertNotEqual(song_another_brick_1, song_clint_eastwood, 'Different songs must not be equal.')
        song_another_brick_3 = Song(name='Another brick in the wall', artist=artist_beatles, album=album_the_wall)
        self.assertNotEqual(song_another_brick_1, song_another_brick_3,
                            'If the artist of the songs differs, they must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(song_another_brick_1), hash(song_another_brick_2),
                         'The hash of two equal songs must be equal.')

    def test_serializable_tag(self):
        """ Tests if the model tag is serializable """
        tag = Tag(name='indie pop')
        tag.save()
        tag_serialized = tag.serialize()
        tag_des = Tag.from_serialized(tag_serialized)
        self.assertEqual(tag_des.id, tag.id, 'The information about the id of the tag shall not be lost.')
        self.assertEqual(tag_des.name, tag.name, 'The information about the tag name shall not be lost.')

    def test_json_encoding_tag(self):
        """  Tests if the model tag can be converted to JSON """
        tag = Tag(name='alternative rock')
        tag.save()
        tag_json = json.dumps(tag, cls=JSONModelEncoder)
        tag_json_load = json.loads(tag_json)
        self.assertEqual(int(tag_json_load['id']), tag.id, 'The information about the id of the tag shall not be lost.')
        self.assertEqual(tag_json_load['name'], tag.name, 'The information about the tag name shall not be lost.')

    def test_serializable_artist(self):
        """ Tests if the model artist is serializable """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1)
        artist_pink_floyd.save()
        artist_pink_floyd_serialized = artist_pink_floyd.serialize()
        artist_pink_floyd_des = artist_pink_floyd.from_serialized(artist_pink_floyd_serialized)
        self.assertEqual(artist_pink_floyd_des.id, artist_pink_floyd.id,
                         'The information about the id of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.name, artist_pink_floyd.name,
                         'The information about the artist name shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.abstract, artist_pink_floyd.abstract,
                         'The information about the artist abstract shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.website, artist_pink_floyd.website,
                         'The information about the artist website shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.city, artist_pink_floyd.city,
                         'The information about the artist city shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.country_code, artist_pink_floyd.country_code,
                         'The information about the country code of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.jamendo_id, artist_pink_floyd.jamendo_id,
                         'The information about the jamendo id of the artist shall not be lost.')

    def test_json_encoding_artist(self):
        """ Tests if the model artist can be converted to JSON """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1)
        artist_pink_floyd.save()
        artist_pink_floyd_json = json.dumps(artist_pink_floyd, cls=JSONModelEncoder)
        artist_pink_floyd_json_load = json.loads(artist_pink_floyd_json)
        self.assertEqual(int(artist_pink_floyd_json_load['id']), artist_pink_floyd.id,
                         'The information about the id of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['name'], artist_pink_floyd.name,
                         'The information about the artist name shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['abstract'], artist_pink_floyd.abstract,
                         'The information about the artist abstract shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['website'], artist_pink_floyd.website,
                         'The information about the artist website shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['city'], artist_pink_floyd.city,
                         'The information about the artist city shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['country_code'], artist_pink_floyd.country_code,
                         'The information about the artist country code shall not be lost.')
        self.assertEqual(int(artist_pink_floyd_json_load['jamendo_id']), artist_pink_floyd.jamendo_id,
                         'The information about the jamendo id of the artist shall not be lost.')

    def test_serializable_album(self):
        """ Tests if the model album is serializable """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1)
        artist_pink_floyd.save()
        album_the_wall = Album(name='The Wall', artist=artist_pink_floyd,
                               release_date=datetime(year=1979, month=10, day=30),
                               jamendo_id=1)
        album_the_wall.save()
        album_the_wall_serialized = album_the_wall.serialize()
        album_the_wall_des = Album.from_serialized(album_the_wall_serialized)
        self.assertEqual(album_the_wall_des.id, album_the_wall.id,
                         'The information about the id of the album shall not be lost.')
        self.assertEqual(album_the_wall_des.name, album_the_wall.name,
                         'The information about the album name shall not be lost.')
        self.assertEqual(album_the_wall_des.artist, album_the_wall.artist,
                         'The information about the artist id of the album shall not be lost.')
        self.assertEqual(album_the_wall_des.release_date, album_the_wall.release_date,
                         'The information about the release date of the album shall not be lost')
        self.assertEqual(album_the_wall_des.jamendo_id, album_the_wall.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

    def test_json_encode_album(self):
        """ """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1)
        artist_pink_floyd.save()
        album_the_wall = Album(name='The Wall', artist=artist_pink_floyd,
                               release_date=datetime(year=1979, month=10, day=30),
                               jamendo_id=1200042)
        album_the_wall.save()
        album_the_wall_json = json.dumps(album_the_wall, cls=JSONModelEncoder)
        album_the_wall_json_load = json.loads(album_the_wall_json)
        self.assertEqual(int(album_the_wall_json_load['id']), album_the_wall.id,
                         'The information about the id of the album shall not be lost.')
        self.assertEqual(album_the_wall_json_load['name'], album_the_wall.name,
                         'The information about the album name shall not be lost.')
        self.assertEqual(int(album_the_wall_json_load['artist']['id']), album_the_wall.artist.id,
                         'The information about the artist id of the album shall not be lost.')
        self.assertEqual(datetime.strptime(album_the_wall_json_load['release_date'], '%Y-%m-%dT%H:%M:%S'),
                         album_the_wall.release_date,
                         'The information about the release date of the album shall not be lost')
        self.assertEqual(int(album_the_wall_json_load['jamendo_id']), album_the_wall.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

    def test_serializable_song(self):
        """ Tests if the model song is serializable """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1200042)
        artist_pink_floyd.save()
        album_the_wall = Album(name='The Wall', artist=artist_pink_floyd,
                               release_date=datetime(year=1979, month=10, day=30),
                               jamendo_id=1)
        album_the_wall.save()
        song_another_brick = Song(name='Another brick in the wall', artist=artist_pink_floyd, album=album_the_wall,
                                  duration=221, release_date=datetime(year=1979, month=10, day=30), jamendo_id=1)
        tag_rock = Tag(name='progressive rock')
        tag_rock.save()
        tag_cult = Tag(name='cult')
        tag_cult.save()
        song_another_brick.save()
        song_another_brick.tags.add(tag_rock, tag_cult)
        song_another_brick.save()
        song_another_brick_serialized = song_another_brick.serialize()
        song_another_brick_des = Song.from_serialized(song_another_brick_serialized)
        self.assertEqual(song_another_brick_des.id, song_another_brick.id,
                         'The information about the id of the album shall not be lost.')
        self.assertEqual(song_another_brick_des.name, song_another_brick.name,
                         'The information about the name of the song shall not be lost.')
        self.assertEqual(song_another_brick_des.duration, song_another_brick.duration,
                         'The information about the duration of the song shall not be lost.')
        self.assertEqual(song_another_brick_des.release_date, song_another_brick.release_date,
                         'The information about the release date of the song shall not be lost.')
        self.assertEqual(song_another_brick_des.album, song_another_brick.album,
                         'The information about the album of the song shall not be lost.')
        self.assertEqual(song_another_brick_des.artist, song_another_brick.artist,
                         'The information about the artist of the song shall not be lost.')
        self.assertListEqual(list(song_another_brick_des.tags.all()), list(song_another_brick.tags.all()),
                             'The information about the tags of the song shall not be lost.')
        self.assertEqual(song_another_brick_des.jamendo_id, song_another_brick.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

    def test_json_encode_song(self):
        """ Tests if the model song can be converted to JSON """
        artist_pink_floyd = Artist(name='Pink Floyd', abstract='This is a abstract.', website='http://pink-floyd.com',
                                   city='London', country_code='UK', jamendo_id=1)
        artist_pink_floyd.save()
        album_the_wall = Album(name='The Wall', artist=artist_pink_floyd,
                               release_date=datetime(year=1979, month=10, day=30),
                               jamendo_id=1)
        album_the_wall.save()
        song_another_brick = Song(name='Another brick in the wall', artist=artist_pink_floyd, album=album_the_wall,
                                  duration=221, release_date=datetime(year=1979, month=10, day=30), jamendo_id=1)
        tag_rock = Tag(name='progressive rock')
        tag_rock.save()
        tag_cult = Tag(name='cult')
        tag_cult.save()
        song_another_brick.save()
        song_another_brick.tags.add(tag_rock, tag_cult)
        song_another_brick.save()
        song_another_brick_json = json.dumps(song_another_brick, cls=JSONModelEncoder)
        song_another_brick_json_load = json.loads(song_another_brick_json)
        self.assertEqual(int(song_another_brick_json_load['id']), song_another_brick.id,
                         'The information about the id of the album shall not be lost.')
        self.assertEqual(song_another_brick_json_load['name'], song_another_brick.name,
                         'The information about the name of the song shall not be lost.')
        self.assertEqual(int(song_another_brick_json_load['duration']), song_another_brick.duration,
                         'The information about the duration of the song shall not be lost.')
        self.assertEqual(datetime.strptime(song_another_brick_json_load['release_date'], '%Y-%m-%dT%H:%M:%S'),
                         song_another_brick.release_date,
                         'The information about the release date of the song shall not be lost.')
        self.assertEqual(int(song_another_brick_json_load['album']['id']), song_another_brick.album.id,
                         'The information about the album of the song shall not be lost.')
        self.assertEqual(int(song_another_brick_json_load['artist']['id']), song_another_brick.artist.id,
                         'The information about the artist of the song shall not be lost.')
        self.assertListEqual([Tag.from_serialized(tag) for tag in song_another_brick_json_load['tags']],
                             list(song_another_brick.tags.all()),
                             'The information about the tags of the song shall not be lost.')
        self.assertEqual(int(song_another_brick_json_load['jamendo_id']), song_another_brick.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

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
