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
import os


def in_functional_testing_mode():
    """
    Checks, if the current server runs in functional testing mode, otherwise false.

    :return: true, if the server runs in functional testing mode, otherwise false.
    """
    return 'FUNCTIONAL_TESTING' in os.environ and os.environ['FUNCTIONAL_TESTING'] == 'True'
