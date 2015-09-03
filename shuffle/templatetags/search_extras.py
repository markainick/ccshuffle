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

from django import template
import math
from urllib.parse import urlencode, parse_qs, urlunparse, urlsplit, urlunsplit, SplitResult

register = template.Library()


@register.filter(name='get_range')
def get_range(value, offset=0):
    """
    Creates a list of integers from the given offset to the given value with the step size 1.

    :param offset: the integer to start the list with (optional). If not given, 0 will be used as start value.
    :param value: the last value of the list.
    :return: returns the list of integers from offset to value (step=1).
    """
    return range(int(offset), int(value))


@register.filter(name='multiply')
def multiply(a, b):
    """
    Computes a * b.

    :param a: the left operand of the multiplication.
    :param b: the right operand of the multiplication.
    :return: a * b
    """
    return a * b


@register.simple_tag(name='search_pagination_url', takes_context=True)
def search_pagination_link_url(context, start):
    """
    Computes for search result requests the link with the given start value. If the url already has a start parameter,
    the current one is replaced by the given one. A ValueError will be thrown, if the given url is no request for a
    search result.

    :param url: the url of the current request.
    :param start: the value, which the start parameter shall have.
    :return: the given url with the new given start parameter.
    """
    scheme, netloc, path, query, fragment = urlsplit(context['request'].get_full_path())
    url_params = parse_qs(query, strict_parsing=False)
    if 'search_phrase' in url_params:
        url_params['search_for'] = url_params['search_for'][0]
        url_params['search_phrase'] = url_params['search_phrase'][0]
        url_params['start'] = start
        query = urlencode(url_params)
        return urlunsplit(SplitResult(scheme=scheme, netloc=netloc, path=path, query=query, fragment=fragment))
    else:
        raise ValueError('The pagination link can only be computed for search result requests !')


@register.inclusion_tag('searchpagination.html', name='search_pagination', takes_context=True)
def pagination_navigation(context, current, max_index, number_of_indexes, min_index=0, step=10):
    """
    A filter for pagination. The filter returns a tuple (lower index, current index, upper index) for the display of
    elegant pagination navigation.

    :param current: the current (activated) index inside of the pagination.
    :param max_index:  the max index number.
    :param number_of_indexes: the indexes, which shall be visible.
    :return: a tuple of (lower index, current index, upper index)
    """
    step = int(step)
    current = int(current)
    min_index = int(min_index)
    max_index = int(max_index)
    number_of_indexes = int(number_of_indexes)
    mini = current - (number_of_indexes / 2) * step
    maxi = current + (number_of_indexes / 2) * step if mini >= 0 else current + (number_of_indexes / 2) * step - mini
    mini -= 0 if maxi <= max_index else (maxi - max_index)
    context.update({
        'pagination_start': math.trunc(max(mini, min_index) / step),
        'pagination_current': math.trunc(current / step),
        'pagination_step': step,
        'pagination_end': math.ceil(min(maxi, max_index) / step)
    })
    return context
