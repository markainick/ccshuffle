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
import time
import logging
import copy
from datetime import datetime
from django.test import TestCase, Client
from ccshuffle.serialize import JSONModelEncoder
from .searchengine import SearchEngine
from .models import Artist, JamendoArtistProfile, Song, JamendoSongProfile, Album, JamendoAlbumProfile, Tag, Source, \
    License

logger = logging.getLogger(__name__)


class HomePageViewTest(TestCase):
    client = Client()


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Test data for the artist model.
        cls.ARTIST_JPROFILE = {
            'The Beatles': JamendoArtistProfile(jamendo_id=1, name='The Beatles',
                                                external_link='https://jamendo.com/beatles'),
            'Pink Floyd': JamendoArtistProfile(jamendo_id=2, name='Pink Floyd',
                                               external_link='https://jamendo.com/beatles/pink-floyd'),
            'Gorillaz': JamendoArtistProfile(jamendo_id=3, name='Pink Floyd',
                                             external_link='https://jamendo.com/gorillaz'),
        }
        for key in cls.ARTIST_JPROFILE:
            cls.ARTIST_JPROFILE[key].save()

        cls.ARTIST_DB = {
            'The Beatles': Artist(name='The Beatles', website='http://the-beatles.org',
                                  jamendo_profile=cls.ARTIST_JPROFILE['The Beatles']),
            'Pink Floyd': Artist(name='Pink Floyd', website='http://pink-floyd.org',
                                 jamendo_profile=cls.ARTIST_JPROFILE['Pink Floyd']),
            'Gorillaz': Artist(name='Gorillaz', website='http://gorillaz.org',
                               jamendo_profile=cls.ARTIST_JPROFILE['Gorillaz']),
        }
        for key in cls.ARTIST_DB:
            cls.ARTIST_DB[key].save()
        # Test data for the album model.
        cls.ALBUM_JPROFILE = {
            'Abbey Road': JamendoAlbumProfile(jamendo_id=1, name='Abbey Road',
                                              cover='https://the-beatles.org/abbey-road-cover'),
            'The Wall': JamendoAlbumProfile(jamendo_id=2, name='The Wall',
                                            cover='https://pink-floyd.org/the-wall-cover'),
            'Demon Days': JamendoAlbumProfile(jamendo_id=3, name='Gorillaz',
                                              cover='https://gorillaz.org/demon-days-cover')
        }
        for key in cls.ALBUM_JPROFILE:
            cls.ALBUM_JPROFILE[key].save()

        cls.ALBUM_DB = {
            'Abbey Road': Album(name='Abbey Road', artist=cls.ARTIST_DB['The Beatles'],
                                release_date=datetime(year=1969, month=9, day=26),
                                jamendo_profile=cls.ALBUM_JPROFILE['Abbey Road']),
            'The Wall': Album(name='The Wall', artist=cls.ARTIST_DB['Pink Floyd'],
                              release_date=datetime(year=1979, month=10, day=30),
                              jamendo_profile=cls.ALBUM_JPROFILE['The Wall']),
            'Gorillaz': Album(name='Demon Days', artist=cls.ARTIST_DB['Gorillaz'],
                              jamendo_profile=cls.ALBUM_JPROFILE['Demon Days']),
        }
        for key in cls.ALBUM_DB:
            cls.ALBUM_DB[key].save()
        # Test data for the model tag.
        cls.TAGS_DB = {
            'indie': Tag(name='indie'),
            'pop': Tag(name='pop'),
            'rock': Tag(name='rock'),
            'progressive rock': Tag(name='progressive rock'),
            'cult': Tag(name='cult'),
            'trip hop': Tag(name='trip hop'),
            'alternativ hop': Tag(name='alternative hop'),
        }
        for key in cls.TAGS_DB:
            cls.TAGS_DB[key].save()
        # Test data for the model license.
        cls.LICENSE_DB = {
            'CC-BY': License(type=License.CC_BY),
            'CC-BY-SA': License(type=License.CC_BY_SA),
            'CC-BY-ND': License(type=License.CC_BY_ND),
            'CC-BY-NC': License(type=License.CC_BY_NC),
            'CC-BY-NC_ND': License(type=License.CC_BY_NC_ND),
            'CC-BY-NC-SA': License(type=License.CC_BY_NC_SA),
        }
        for key in cls.LICENSE_DB:
            cls.LICENSE_DB[key].save()
        # Test data for the model song.
        cls.SONG_JPROFILE = {
            'Clint Eastwood': JamendoSongProfile(jamendo_id=1, name='Clint Eastwood (Single)',
                                                 cover='https://gorillaz.org/demon-days-cover'),
            'Another brick in the wall': JamendoSongProfile(jamendo_id=2, name='Another brick in the wall',
                                                            cover='https://pink-floyd.org/the-wall-cover'),
        }
        for key in cls.SONG_JPROFILE:
            cls.SONG_JPROFILE[key].save()

        cls.SONG_DB = {
            'Clint Eastwood': Song(name='Clint Eastwood (Single)', artist=cls.ARTIST_DB['Gorillaz'], duration=274,
                                   license=cls.LICENSE_DB['CC-BY'],
                                   jamendo_profile=cls.SONG_JPROFILE['Clint Eastwood']),
            'Another brick in the wall': Song(name='Another brick in the wall', artist=cls.ARTIST_DB['Pink Floyd'],
                                              album=cls.ALBUM_DB['The Wall'], duration=191,
                                              license=cls.LICENSE_DB['CC-BY-NC-SA'],
                                              release_date=datetime(year=1979, month=10, day=30),
                                              jamendo_profile=cls.SONG_JPROFILE['Another brick in the wall']),
        }
        for key in cls.SONG_DB:
            cls.SONG_DB[key].save()
        cls.SONG_DB['Another brick in the wall'].tags.add(cls.TAGS_DB['progressive rock'], cls.TAGS_DB['cult'])
        cls.SONG_DB['Clint Eastwood'].tags.add(cls.TAGS_DB['trip hop'], cls.TAGS_DB['alternativ hop'])
        # Test data for the model source.
        cls.SOURCE_DB = {
            'CE: MP3 Download': Source(type=Source.TYPE_DOWNLOAD, song=cls.SONG_DB['Clint Eastwood'],
                                       link='http://clint-eastwood.org/audio.mp3', codec=Source.CODEC_MP3),
            'CE OGG Stream': Source(type=Source.TYPE_STREAM, song=cls.SONG_DB['Clint Eastwood'],
                                    link='http://clint-eastwood.stream/audio.ogg', codec=Source.CODEC_OGG),
            'ABITW MP3 Download': Source(type=Source.TYPE_STREAM, song=cls.SONG_DB['Another brick in the wall'],
                                         codec=Source.CODEC_MP3, link='http://stream-link.org/audio.mp3'),
            'ABITW OGG Download': Source(type=Source.TYPE_DOWNLOAD, song=cls.SONG_DB['Another brick in the wall'],
                                         codec=Source.CODEC_OGG, link='http://stream-link.org/audio.ogg'),
            'ABITW MP3 Stream': Source(type=Source.TYPE_STREAM, song=cls.SONG_DB['Another brick in the wall'],
                                       codec=Source.CODEC_MP3, link='http://stream-link.stream/audio.mp3'),
            'ABITW OGG Stream': Source(type=Source.TYPE_STREAM, song=cls.SONG_DB['Another brick in the wall'],
                                       codec=Source.CODEC_OGG, link='http://stream-link.stream/audio.ogg'),
        }
        for key in cls.SOURCE_DB:
            cls.SOURCE_DB[key].save()

    def test_eq_hash_license(self):
        license_cc_by_1 = self.LICENSE_DB['CC-BY']
        license_cc_by_2 = copy.deepcopy(license_cc_by_1)
        self.assertEqual(license_cc_by_1, license_cc_by_2, 'Licenses with the same type must be equal.')
        license_cc_by_sa_1 = self.LICENSE_DB['CC-BY-SA']
        self.assertNotEqual(license_cc_by_1, license_cc_by_sa_1, 'Licenses with different types must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(license_cc_by_1), hash(license_cc_by_2),
                         'The hash value of equal licenses must be the same.')

    def test_eq_hash_tag(self):
        tag_indie_rock_1 = self.TAGS_DB['indie']
        tag_indie_rock_2 = copy.deepcopy(self.TAGS_DB['indie'])
        self.assertEqual(tag_indie_rock_1, tag_indie_rock_2, 'Tags with the same name must be equal.')
        tag_pop = self.TAGS_DB['pop']
        self.assertNotEqual(tag_indie_rock_1, tag_pop, 'Tags with different names must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(tag_indie_rock_1), hash(tag_indie_rock_2),
                         'The has value of tags with the same name must be equal.')

    def test_eq_hash_source(self):
        source_1 = self.SOURCE_DB['ABITW MP3 Stream']
        source_2 = copy.deepcopy(self.SOURCE_DB['ABITW MP3 Stream'])
        self.assertEqual(source_1, source_2, 'Sources with the same type, link and codec must be equal.')
        source_2.link = 'http://source-link.org/audio.ogg'
        source_2.codec = Source.CODEC_OGG
        self.assertNotEqual(source_1, source_2, 'Sources with different typ, link or codec must not be equal.')

    def test_eq_hash_jamendo_artist_profile(self):
        artist_jprofile_1 = self.ARTIST_JPROFILE['The Beatles']
        artist_jprofile_2 = copy.deepcopy(artist_jprofile_1)
        self.assertEqual(artist_jprofile_1, artist_jprofile_2,
                         'Artists with the jamendo profile (id) must be equal.')
        artist_jprofile_3 = copy.deepcopy(artist_jprofile_2)
        artist_jprofile_3.jamendo_id = 99
        self.assertNotEqual(artist_jprofile_1, artist_jprofile_3,
                            'Artists with different jamendo profile (id) must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(artist_jprofile_1), hash(artist_jprofile_2),
                         'The hash of two equal artists must be equal.')

    def test_eq_hash_artists(self):
        artist_beatles_1 = self.ARTIST_DB['The Beatles']
        artist_beatles_2 = copy.deepcopy(self.ARTIST_DB['The Beatles'])
        self.assertEqual(artist_beatles_1, artist_beatles_2, 'Artists with the same name must be equal.')
        artist_pink_floyd_1 = self.ARTIST_DB['Pink Floyd']
        self.assertNotEqual(artist_pink_floyd_1, artist_beatles_1,
                            'Artists with the different names must not be equal.')
        artist_pink_floyd_2 = copy.deepcopy(self.ARTIST_DB['Pink Floyd'])
        self.assertEqual(artist_pink_floyd_1, artist_pink_floyd_2,
                         'Artists with the same name and service id must be equal.')
        artist_pink_floyd_2.jamendo_profile.jamendo_id = 10
        self.assertNotEqual(artist_pink_floyd_1, artist_pink_floyd_2,
                            'If the jamendo id differs, the artists must not be equal (also if they have the same)')
        # Tests the hashing.
        self.assertEqual(hash(artist_beatles_1), hash(artist_beatles_2), 'The hash of two equal artists must be equal.')

    def test_eq_hash_jamendo_album_profile(self):
        album_jprofile_1 = self.ALBUM_JPROFILE['The Wall']
        album_jprofile_2 = copy.deepcopy(album_jprofile_1)
        self.assertEqual(album_jprofile_1, album_jprofile_2,
                         'The albums with the same jamendo profile (id) must be equal.')
        album_jprofile_3 = copy.deepcopy(album_jprofile_2)
        album_jprofile_3.jamendo_id = 99
        self.assertNotEqual(album_jprofile_1, album_jprofile_3,
                            'The albums with different jamendo id must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(album_jprofile_1), hash(album_jprofile_2), 'The hash of two equal artists must be equal.')

    def test_eq_hash_albums(self):
        album_abbey_road_1 = self.ALBUM_DB['Abbey Road']
        album_abbey_road_2 = copy.deepcopy(self.ALBUM_DB['Abbey Road'])
        album_abbey_road_2.jamendo_profile = None
        self.assertEqual(album_abbey_road_1, album_abbey_road_2, 'Albums with the same name and artist must be equal.')
        album_abbey_road_2.artist = self.ARTIST_DB['Pink Floyd']
        self.assertNotEqual(album_abbey_road_1, album_abbey_road_2,
                            'If the artist differs, the albums must not be equal.')
        album_the_wall_1 = self.ALBUM_DB['The Wall']
        album_the_wall_2 = copy.deepcopy(self.ALBUM_DB['The Wall'])
        self.assertEqual(album_the_wall_1, album_the_wall_2,
                         'If the name and service ids of the albums are the same, they must be equal.')
        album_the_wall_2.jamendo_profile.jamendo_id = 4
        self.assertNotEqual(album_the_wall_1, album_the_wall_2,
                            'If one of the service id differs, the albums must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(album_abbey_road_1), hash(copy.deepcopy(self.ALBUM_DB['Abbey Road'])),
                         'The hash of two equal albums must be equal.')

    def test_eq_hash_jamendo_song_profile(self):
        song_another_brick_jprofile_1 = self.SONG_JPROFILE['Another brick in the wall']
        song_another_brick_jprofile_2 = copy.deepcopy(song_another_brick_jprofile_1)
        self.assertEqual(song_another_brick_jprofile_1, song_another_brick_jprofile_2,
                         'The song profiles with the same jamendo id must be equal.')
        song_another_brick_jprofile_3 = copy.deepcopy(song_another_brick_jprofile_2)
        song_another_brick_jprofile_3.jamendo_id = 99
        self.assertNotEqual(song_another_brick_jprofile_1, song_another_brick_jprofile_3,
                            'The song profiles with different jamendo id must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(song_another_brick_jprofile_1), hash(song_another_brick_jprofile_2),
                         'The hash of two equal artists must be equal.')

    def test_eq_hash_songs(self):
        song_another_brick_1 = self.SONG_DB['Another brick in the wall']
        song_another_brick_2 = copy.deepcopy(self.SONG_DB['Another brick in the wall'])
        self.assertEqual(song_another_brick_1, song_another_brick_2,
                         'The song with same name, artist and album must be equal.')
        song_clint_eastwood_1 = self.SONG_DB['Clint Eastwood']
        song_clint_eastwood_2 = copy.deepcopy(self.SONG_DB['Clint Eastwood'])
        self.assertEqual(song_clint_eastwood_1, song_clint_eastwood_2,
                         'Singles with the same name and artist must be the same.')
        self.assertNotEqual(song_another_brick_1, song_clint_eastwood_2, 'Different songs must not be equal.')
        song_another_brick_3 = copy.deepcopy(song_another_brick_2)
        song_another_brick_3.artist = self.ARTIST_DB['The Beatles']
        self.assertNotEqual(song_another_brick_1, song_another_brick_3,
                            'If the artist of the songs differs, they must not be equal.')
        # Tests the hashing.
        self.assertEqual(hash(song_another_brick_1), hash(song_another_brick_2),
                         'The hash of two equal songs must be equal.')

    def test_serializable_license(self):
        license_cc_by = self.LICENSE_DB['CC-BY']
        license_cc_by_serialized = license_cc_by.serialize()
        license_cc_by_des = License.from_serialized(license_cc_by_serialized)
        self.assertEqual(license_cc_by_des.id, license_cc_by.id, 'The information about the id shall not be lost')
        self.assertEqual(license_cc_by_des.type, license_cc_by.type, 'The information about the type shall not be lost')

    def test_json_encoding_license(self):
        license_cc_sa = self.LICENSE_DB['CC-BY-SA']
        license_cc_sa_json = json.dumps(license_cc_sa, cls=JSONModelEncoder)
        license_cc_sa_load = json.loads(license_cc_sa_json)
        self.assertEqual(int(license_cc_sa_load['id']), license_cc_sa.id,
                         'The information about the id shall not be lost.')
        self.assertEqual(license_cc_sa_load['type'], license_cc_sa.type,
                         'The information about the type shall not be lost')

    def test_serializable_tag(self):
        tag = Tag(name='indie pop')
        tag.save()
        tag_serialized = tag.serialize()
        tag_des = Tag.from_serialized(tag_serialized)
        self.assertEqual(tag_des.id, tag.id, 'The information about the id of the tag shall not be lost.')
        self.assertEqual(tag_des.name, tag.name, 'The information about the tag name shall not be lost.')

    def test_json_encoding_tag(self):
        tag = Tag(name='alternative rock')
        tag.save()
        tag_json = json.dumps(tag, cls=JSONModelEncoder)
        tag_json_load = json.loads(tag_json)
        self.assertEqual(int(tag_json_load['id']), tag.id, 'The information about the id of the tag shall not be lost.')
        self.assertEqual(tag_json_load['name'], tag.name, 'The information about the tag name shall not be lost.')

    def test_serializable_source(self):
        source = self.SOURCE_DB['ABITW OGG Download']
        source_serialized = source.serialize()
        source_des = Source.from_serialized(source_serialized)
        self.assertEqual(source_des.id, source.id, 'The id of the source shall not be lost.')
        self.assertEqual(source_des.type, source.type, 'The type of the source shall not be lost.')
        self.assertEqual(source_des.song, source.song, 'The song of the source shall not be lost.')
        self.assertEqual(source_des.link, source.link, 'The link of the source shall not be lost.')
        self.assertEqual(source_des.codec, source.codec, 'The codec of the source shall not be lost.')

    def test_json_encoding_source(self):
        source = self.SOURCE_DB['CE OGG Stream']
        source_json = json.dumps(source, cls=JSONModelEncoder)
        source_loaded = json.loads(source_json)
        self.assertEqual(int(source_loaded['id']), source.id, 'The id of the source shall not be lost.')
        self.assertEqual(source_loaded['type'], source.type, 'The type of the source shall not be lost.')
        self.assertEqual(int(source_loaded['song_id']), source.song.id,
                         'The song (id) of the source shall not be lost.')
        self.assertEqual(source_loaded['link'], source.link, 'The link of the source shall not be lost.')
        self.assertEqual(source_loaded['codec'], source.codec, 'The codec of the source shall not be lost.')

    def test_serializable_artist_jamendo_profile(self):
        artist_the_beatles_jprofile = self.ARTIST_JPROFILE['The Beatles']
        artist_the_beatles_jprofile_des = JamendoArtistProfile.from_serialized(artist_the_beatles_jprofile.serialize())
        self.assertEqual(artist_the_beatles_jprofile.jamendo_id, artist_the_beatles_jprofile_des.jamendo_id,
                         'The information about the jamendo id shall be lost.')
        self.assertEqual(artist_the_beatles_jprofile.name, artist_the_beatles_jprofile_des.name,
                         'The information about the name shall not be lost.')
        self.assertEqual(artist_the_beatles_jprofile.image, artist_the_beatles_jprofile_des.image,
                         'The information about the image link shall not be lost.')
        self.assertEqual(artist_the_beatles_jprofile.external_link, artist_the_beatles_jprofile_des.external_link,
                         'The information about the external link shall not be lost.')

    def test_json_encoding_artist_jamendo_profile(self):
        artist_gorillaz_jprofile = self.ARTIST_JPROFILE['Gorillaz']
        artist_gorillaz_jprofile_json = json.dumps(artist_gorillaz_jprofile, cls=JSONModelEncoder)
        artist_gorillaz_jprofile_loads = json.loads(artist_gorillaz_jprofile_json)
        self.assertEqual(artist_gorillaz_jprofile.jamendo_id, int(artist_gorillaz_jprofile_loads['jamendo_id']),
                         'The information about the jamendo id shall be lost.')
        self.assertEqual(artist_gorillaz_jprofile.name, artist_gorillaz_jprofile_loads['name'],
                         'The information about the name shall not be lost.')
        self.assertEqual(artist_gorillaz_jprofile.image, artist_gorillaz_jprofile_loads['image'],
                         'The information about the image link shall not be lost.')
        self.assertEqual(artist_gorillaz_jprofile.external_link, artist_gorillaz_jprofile_loads['external_link'],
                         'The information about the external link shall not be lost.')

    def test_serializable_artist(self):
        artist_pink_floyd = self.ARTIST_DB['Pink Floyd']
        artist_pink_floyd_serialized = artist_pink_floyd.serialize()
        artist_pink_floyd_des = artist_pink_floyd.from_serialized(artist_pink_floyd_serialized)
        self.assertEqual(artist_pink_floyd_des.id, artist_pink_floyd.id,
                         'The information about the id of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.name, artist_pink_floyd.name,
                         'The information about the artist name shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.website, artist_pink_floyd.website,
                         'The information about the website shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.abstract, artist_pink_floyd.abstract,
                         'The information about the artist abstract shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.city, artist_pink_floyd.city,
                         'The information about the artist city shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.country_code, artist_pink_floyd.country_code,
                         'The information about the country code of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_des.jamendo_id, artist_pink_floyd.jamendo_id,
                         'The information about the jamendo id of the artist shall not be lost.')

    def test_json_encoding_artist(self):
        artist_pink_floyd = self.ARTIST_DB['Pink Floyd']
        artist_pink_floyd_json = json.dumps(artist_pink_floyd, cls=JSONModelEncoder)
        artist_pink_floyd_json_load = json.loads(artist_pink_floyd_json)
        self.assertEqual(int(artist_pink_floyd_json_load['id']), artist_pink_floyd.id,
                         'The information about the id of the artist shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['name'], artist_pink_floyd.name,
                         'The information about the artist name shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['website'], artist_pink_floyd.website,
                         'The information about the website shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['abstract'], artist_pink_floyd.abstract,
                         'The information about the artist abstract shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['city'], artist_pink_floyd.city,
                         'The information about the artist city shall not be lost.')
        self.assertEqual(artist_pink_floyd_json_load['country_code'], artist_pink_floyd.country_code,
                         'The information about the artist country code shall not be lost.')
        self.assertEqual(int(artist_pink_floyd_json_load['jamendo_profile']['jamendo_id']),
                         artist_pink_floyd.jamendo_id,
                         'The information about the jamendo id of the artist shall not be lost.')

    def test_eq_hash_album_jamendo_profile(self):
        album_abbey_road_jprofile = self.ALBUM_JPROFILE['Abbey Road']
        album_abbey_road_jprofile_des = JamendoAlbumProfile.from_serialized(album_abbey_road_jprofile.serialize())
        self.assertEqual(album_abbey_road_jprofile.jamendo_id, album_abbey_road_jprofile_des.jamendo_id,
                         'The information about the jamendo id shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.name, album_abbey_road_jprofile_des.name,
                         'The information about the name of the album shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.cover, album_abbey_road_jprofile_des.cover,
                         'The information about the cover link shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.external_link, album_abbey_road_jprofile_des.external_link,
                         'The information about the external link shall not be lost.')

    def test_json_encode_album_jamendo_profile(self):
        album_abbey_road_jprofile = self.ALBUM_JPROFILE['Abbey Road']
        album_abbey_road_jprofile_json = json.dumps(album_abbey_road_jprofile, cls=JSONModelEncoder)
        album_abbey_road_jprofile_json_load = json.loads(album_abbey_road_jprofile_json)
        self.assertEqual(album_abbey_road_jprofile.jamendo_id, int(album_abbey_road_jprofile_json_load['jamendo_id']),
                         'The information about the jamendo id shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.name, album_abbey_road_jprofile_json_load['name'],
                         'The information about the name of the album shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.cover, album_abbey_road_jprofile_json_load['cover'],
                         'The information about the cover link shall not be lost.')
        self.assertEqual(album_abbey_road_jprofile.external_link, album_abbey_road_jprofile_json_load['external_link'],
                         'The information about the external link shall not be lost.')

    def test_serializable_album(self):
        album_the_wall = self.ALBUM_DB['The Wall']
        album_the_wall_des = Album.from_serialized(album_the_wall.serialize())
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

    def test_serializable_song_jamendo_profile(self):
        song_clint_eastwood_jprofile = self.SONG_JPROFILE['Clint Eastwood']
        song_clint_eastwood_jprofile_des = JamendoSongProfile.from_serialized(song_clint_eastwood_jprofile.serialize())
        self.assertEqual(song_clint_eastwood_jprofile.jamendo_id, song_clint_eastwood_jprofile_des.jamendo_id,
                         'The information about the jamendo id shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.name, song_clint_eastwood_jprofile_des.name,
                         'The information about the name shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.cover, song_clint_eastwood_jprofile_des.cover,
                         'The information about the cover link shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.external_link, song_clint_eastwood_jprofile_des.external_link,
                         'The information about the external link shall not be lost.')

    def test_json_encode_song_jamendo_profile(self):
        song_clint_eastwood_jprofile = self.SONG_JPROFILE['Clint Eastwood']
        song_clint_eastwood_jprofile_json = json.dumps(song_clint_eastwood_jprofile, cls=JSONModelEncoder)
        song_clint_eastwood_jprofile_json_loads = json.loads(song_clint_eastwood_jprofile_json)
        self.assertEqual(song_clint_eastwood_jprofile.jamendo_id,
                         int(song_clint_eastwood_jprofile_json_loads['jamendo_id']),
                         'The information about the jamendo id shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.name, song_clint_eastwood_jprofile_json_loads['name'],
                         'The information about the name shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.cover, song_clint_eastwood_jprofile_json_loads['cover'],
                         'The information about the cover link shall not be lost.')
        self.assertEqual(song_clint_eastwood_jprofile.external_link,
                         song_clint_eastwood_jprofile_json_loads['external_link'],
                         'The information about the external link shall not be lost.')

    def test_json_encode_album(self):
        album_the_wall = self.ALBUM_DB['The Wall']
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
        self.assertEqual(int(album_the_wall_json_load['jamendo_profile']['jamendo_id']), album_the_wall.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

    def test_serializable_song(self):
        song_another_brick = self.SONG_DB['Another brick in the wall']
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
        song_another_brick = self.SONG_DB['Another brick in the wall']
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
        self.assertEqual(int(song_another_brick_json_load['jamendo_profile']['jamendo_id']),
                         song_another_brick.jamendo_id,
                         'The information about the jamendo id of the album shall not be lost.')

    def test_sources_of_song(self):
        song_another_brick = self.SONG_DB['Another brick in the wall']
        self.assertIn(self.SOURCE_DB['ABITW MP3 Download'], song_another_brick.sources(codec=Source.CODEC_MP3),
                      'The MP3 download source must be returned.')
        self.assertIn(self.SOURCE_DB['ABITW MP3 Stream'], song_another_brick.sources(codec=Source.CODEC_MP3),
                      'The MP3 stream source must be returned.')
        self.assertIn(self.SOURCE_DB['ABITW OGG Download'], song_another_brick.sources(codec=Source.CODEC_OGG),
                      'The OGG download source must be returned.')
        self.assertIn(self.SOURCE_DB['ABITW OGG Stream'], song_another_brick.sources(codec=Source.CODEC_OGG),
                      'The OGG stream source must be returned.')
        # Tests the source method (codec & type)
        self.assertEqual(len(song_another_brick.sources(type=Source.TYPE_STREAM, codec=Source.CODEC_OGG)), 1,
                         'Only the ogg stream source must be returned.')
        self.assertEqual(self.SOURCE_DB['ABITW OGG Stream'],
                         song_another_brick.sources(type=Source.TYPE_STREAM, codec=Source.CODEC_OGG)[0],
                         'The OGG stream must be returned as only one.')
        # All sources.
        sources_saved = [self.SOURCE_DB['ABITW MP3 Download'], self.SOURCE_DB['ABITW OGG Download'],
                         self.SOURCE_DB['ABITW MP3 Stream'], self.SOURCE_DB['ABITW OGG Stream']]
        sources_from_db = song_another_brick.sources()
        for source in sources_from_db:
            self.assertIn(source, sources_saved)
            sources_saved.remove(source)
        self.assertEqual(len(sources_saved), 0, 'All sources of the song \'Another brick in the wall \'')


class SearchEngineTest(TestCase):
    fixtures = ['fixtures/se_test_db.json']

    def __measure(self, func, *args, **kwargs):
        """
        Measures and returns the execution time  of the given function.

        :param func: the function, which shall be measured.
        :param args: the positional arguments of the given function.
        :param kwargs: the keyword arguments of the given function.
        :return: the execution time.
        """
        start = time.time()
        func(*args, **kwargs)
        return time.time() - start

    def __performance(self, func, *args, iterations=100, **kwargs):
        """
        Tests the performance of the function and returns the average, as
        well as the minimum and maximum execution time. The returned type is
        a tuple (min, avg, max).

        :param func: the function, of which the performance shall be checked.
        :param args: the positional arguments of the given function.
        :param kwargs: the keyword arguments of the given function.
        :return: the performance.
        """
        avg = None
        min = 10 ** 1000
        max = 0
        for n in range(iterations):
            exe_time = self.__measure(func, *args, **kwargs)
            avg = (exe_time if avg is None else (avg + exe_time) / 2)
            min = (min if min <= exe_time else exe_time)
            max = (max if max >= exe_time else exe_time)
            time.sleep(0.1)
        return min, avg, max

    def test_search_songs_extracted_tags(self):
        """
        Tests, if the tags of search phrases are encapsulated correctly.
        """
        # Search phrase: 'Jazz is my love'
        search_request = SearchEngine.SearchRequest(search_phrase='Jazz is my love',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        se_tags_in_search_phrase = SearchEngine.accept(search_request).extracted_tags
        self.assertIn('jazz', se_tags_in_search_phrase, 'The tag \'jazz\' must be returned.')
        self.assertIn('love', se_tags_in_search_phrase, 'The tag \'love\' must be returned.')
        # Search phrase: 'forever indie rock!'
        search_request = SearchEngine.SearchRequest(search_phrase='forever indie rock!',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        se_tags_in_search_phrase = SearchEngine.accept(search_request).extracted_tags
        self.assertIn('indie', se_tags_in_search_phrase, 'The tag \'indie\' must be returned.')
        self.assertIn('rock', se_tags_in_search_phrase, 'The tag \'rock\' must be returned.')

    def test_search_songs(self):
        """
        Tests, if the search for songs works correctly.
        """
        # Search phrase: 'rock Indie alternative'
        search_request = SearchEngine.SearchRequest(search_phrase='rock Indie alternative',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        search_result = SearchEngine.accept(search_request).search_result
        self.assertIn('punk storm mario', [song.name.lower() for song in search_result],
                      '\'Punk storm mario\' must be in the search result (search phrase: %s).' % search_request.search_phrase)
        self.assertIn('land of a beautiful experience', [song.name.lower() for song in search_result],
                      '\'land of a beautiful experience\' must be in the search result (search phrase: %s).' % search_request.search_phrase)
        # Search phrase: 'Jazz is my love'
        search_request = SearchEngine.SearchRequest(search_phrase='Jazz is my love',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        search_result = SearchEngine.accept(search_request).search_result
        self.assertIn('i see beauty', [song.name.lower() for song in search_result],
                      '\'i see beauty\' must be in the search result (search phrase: %s).' % search_request.search_phrase)
        self.assertIn('moonlight dance', [song.name.lower() for song in search_result],
                      '\'moonlight dance\' must be in the search result (search phrase: %s).' % search_request.search_phrase)
        # Search phrase: 'Long dreams, short nights'
        search_request = SearchEngine.SearchRequest(search_phrase='Long dreams, short nights',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        search_result = SearchEngine.accept(search_request).search_result
        self.assertIn('the night drives the wolf', [song.name.lower() for song in search_result],
                      '\'the night drives the wolf\' must be in the search result (search phrase: %s).' % search_request.search_phrase)
        self.assertIn('long dreams, short nights', [song.name.lower() for song in search_result],
                      '\'long dreams, short nights\' must be in the search result (search phrase: %s).' % search_request.search_phrase)

    def __search_song(self, search_phrase, search_for):
        """ Wrapper-function for testing the performance of the search."""
        search_request = SearchEngine.SearchRequest(search_phrase=search_phrase, search_for=search_for)
        return list(SearchEngine.accept(search_request))

    def test_performance_search_songs(self):
        """
        Tests the performance of searching a song. The average response time must be under 1 second for the
        test database.
        """
        response_times = self.__performance(
            func=self.__search_song, search_phrase='Jazz is my love', search_for=SearchEngine.SEARCH_FOR_SONGS)
        self.assertLess(response_times[2], 1.5, 'The peek of the response time must be less than 1.5 seconds.')
        self.assertLess(response_times[1], 1.0, 'The average of the response time must be less than 1.0 seconds.')

    def test_caching_search_request(self):
        search_request = SearchEngine.SearchRequest(search_phrase='indie rock alternative',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        search_engine = SearchEngine()
        search_engine.SearchCache._cache_time_s = 8000
        search_response = search_engine.accept(search_request)
        time.sleep(2)
        self.assertEqual(search_response, search_engine.search_cache.get(search_request),
                         'The search response, which has been stored to the cache, must be equal to the search response returned by the cache with the get-method (if the timestamp is not too old).')

    def test_caching_search_requests_old_timestamp(self):
        """
        Tests if the stored search result will be deleted or overwritten (by the response to a new request), if the
        caching time was overrun.
        """
        search_request = SearchEngine.SearchRequest(search_phrase='indie rock alternative',
                                                    search_for=SearchEngine.SEARCH_FOR_SONGS)
        search_engine = SearchEngine()
        search_engine.SearchCache._cache_time_s = 1000
        search_engine.accept(search_request)
        time.sleep(1.1)
        self.assertIsNone(search_engine.search_cache.get(search_request),
                          'The cache of the search engine must return None, if the timestamp of the stored search response is too old.')
