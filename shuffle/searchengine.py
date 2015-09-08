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
from collections import namedtuple
from datetime import datetime, timedelta
import logging
import copy

logger = logging.getLogger(__name__)


class SearchEngine(object):
    SEARCH_FOR_SONGS = 'songs'
    SEARCH_FOR_ALBUMS = 'albums'
    SEARCH_FOR_ARTISTS = 'artists'

    SEARCH_FOR = {
        SEARCH_FOR_SONGS: Song,
        SEARCH_FOR_ALBUMS: Album,
        SEARCH_FOR_ARTISTS: Artist,
    }

    class SearchRequest(object):
        """ This class represents a search request, which consists of the search phrase and search for type. """

        def __init__(self, search_phrase:str='', search_for:str='songs'):
            assert search_for in SearchEngine.SEARCH_FOR
            self.search_phrase = search_phrase
            self.search_for = search_for
            self.timestamp = datetime.now()

        def __eq__(self, other) -> bool:
            if isinstance(other, type(self)):
                return self.search_phrase == other.search_phrase and self.search_for == other.search_for
            else:
                return False

        def __hash__(self) -> int:
            return hash(self.search_phrase) ^ hash(self.search_for)

        def __repr__(self) -> str:
            return '<Search-Request: %s, %s>' % (self.search_phrase, self.search_for)

    class SearchResponse(namedtuple('SearchResponse', ['search_result', 'extracted_tags'])):
        """
        This class represents the response to a search request, which consist of the search result and the
        extracted tags of the search phrase of the search request.
        """

        def __eq__(self, other) -> bool:
            if isinstance(other, type(self)):
                return self.search_result == other.search_result
            else:
                return False

        def __hash__(self) -> int:
            return hash(self.search_result)

    class SearchCache(object):
        """ This class represents a possibility to cache search results for a search request temporarily. """

        _cache_time_s = 3600

        def __init__(self):
            self.search_cache = dict()

        def push(self, search_request, search_response) -> None:
            """
            Pushes the given search response to this cache. The given search request is used as key to access the search
            response.

            :param search_request: the search request (key), which is used to access the given search result .
            :param search_response: the result of the given search request (value).
            """
            self.search_cache[copy.deepcopy(search_request)] = (search_response, search_request.timestamp)

        def get(self, search_request):
            """
            The stored search result of the given request will be returned, if it has been cached and is valid.
            Otherwise None will be returned.

            :param search_request: the search request, of which the search result shall be returned.
            :return: the stored search result of the given request will be returned, if it was cached and is valid -
            otherwise None.
            """
            if search_request in self.search_cache:
                search_result, timestamp = self.search_cache[search_request]
                if datetime.now() - timedelta(seconds=self._cache_time_s) < timestamp:
                    return search_result
                else:
                    del self.search_cache[search_request]
            return None

    search_cache = SearchCache()

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
    def __extract_tags_of(cls, search_phrase: str) -> [str]:
        """
        Analysis the given search phrase and returns the tags, which were found in the given search phrase.

        :param search_phrase: the search phrase, of which the tags shall be encapsulated.
        :return: the tags of the given search phrase.
        """
        known_tags_names = cls.all_tags_names()
        return [tag.lower() for tag in search_phrase.split(' ') if tag.lower() in known_tags_names]

    @classmethod
    def accept(cls, search_request) -> ([SearchableModel], [str]):
        """
        Accepts the search request. If the response of this request is stored in the cache, the stored response will
        be returned, otherwise the persistent source (database, ..) is queried.

        :param search_request: the search request to search for.
        :return: the search response of the search request.
        """
        if search_request:
            search_response = cls.search_cache.get(search_request)
            if search_response is None:
                search_tags = cls.__extract_tags_of(search_request.search_phrase)
                search_result = cls.SEARCH_FOR[search_request.search_for].search(search_request.search_phrase,
                                                                                 search_tags)
                search_response = cls.SearchResponse(search_result=search_result, extracted_tags=search_tags)
                cls.search_cache.push(search_request, search_response)
            return search_response
        else:
            raise ValueError('The given search request must not be None !' % search_request)
