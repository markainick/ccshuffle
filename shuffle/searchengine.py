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

from .models import SearchableModel, Song, Artist, Album, Tag
import logging

logger = logging.getLogger(__name__)


class SearchEngine(object):
    """ The class represents the search engine """

    SEARCH_FOR_SONGS = 'songs'
    SEARCH_FOR_ALBUMS = 'albums'
    SEARCH_FOR_ARTISTS = 'artists'

    SEARCH_FOR = {
        SEARCH_FOR_SONGS: Song,
        SEARCH_FOR_ALBUMS: Album,
        SEARCH_FOR_ARTISTS: Artist,
    }

    @classmethod
    def all_tags(cls) -> [Tag]:
        """
        Returns all known tags.

        :return: all known tags.
        """
        return set(Tag.objects.all())

    @classmethod
    def all_tags_names(cls) -> [str]:
        """
        Returns all known tags in form of their names.

        :return: all known tags in form of their names.
        """
        return [tag_name[0] for tag_name in Tag.objects.values_list('name')]

    @classmethod
    def __encapsulate_tags_of(cls, search_phrase: str) -> [str]:
        """
        Analysis the given search phrase and returns the tags, which were found in the given search phrase.

        :param search_phrase: the search phrase, of which the tags shall be encapsulated.
        :return: the tags of the given search phrase.
        """
        known_tags_names = cls.all_tags_names()
        return [tag.lower() for tag in search_phrase.split(' ') if tag.lower() in known_tags_names]

    @classmethod
    def __search_for_albums(cls, search_phrase: str, search_tags: [str]) -> [Album]:
        """
        Searches for albums, which matches the given search phrase.

        :param search_phrase: the search phrase, which the albums shall match.
        :param search_tags: the tags, which the albums shall match.
        :return: albums, which match the given search phrase.
        """
        raise NotImplementedError('Not implemented yet !')

    @classmethod
    def __search_for_artists(cls, search_phrase: str, search_tags: [str]) -> [Artist]:
        """
        Searches for artists, which matches the given search phrase.

        :param search_phrase: the search phrase, which the artists shall match.
        :param search_tags: the tags, which the artists shall match.
        :return: artists, which match the given search phrase.
        """
        raise NotImplementedError('Not implemented yet !')

    @classmethod
    def __search_for_songs(cls, search_phrase: str, search_tags: [str]) -> [Song]:
        """
        Searches for songs, which matches the given search phrase.

        :param search_phrase: the search phrase, which shall match.
        :param search_tags: the tags, which the songs shall match.
        :return: songs, which match the given search phrase.
        """
        return Song.search(search_phrase, search_tags)

    @classmethod
    def search(cls, search_phrase: str='', search_for: str=SEARCH_FOR_SONGS) -> ([SearchableModel], [str]):
        """
        Searches for the given search_for type (tags, albums, artists, songs), which fulfills the given search phrase.

        :param search_phrase: the search phrase.
        :param search_for: the search type (tags, albums, artists, songs).
        :return: the search result and the encapsulated tags in form of a tuple.
        """
        if search_for == cls.SEARCH_FOR_SONGS:
            search_tags = cls.__encapsulate_tags_of(search_phrase)
            return cls.__search_for_songs(search_phrase, search_tags), search_tags
        elif search_for == cls.SEARCH_FOR_ALBUMS:
            search_tags = cls.__encapsulate_tags_of(search_phrase)
            return cls.__search_for_albums(search_phrase, search_tags), search_tags
        elif search_for == cls.SEARCH_FOR_ARTISTS:
            search_tags = cls.__encapsulate_tags_of(search_phrase)
            return cls.__search_for_artists(search_phrase, search_tags), search_tags
        else:
            raise ValueError('The given search type (%s) is unknown !' % search_for)
