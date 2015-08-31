#!/usr/bin/env python

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
import random
import string
from ccshuffle import settings


def generate_password(length=8, numeric=True, special_chars=''):
    """
    Generates a password with the given length, consisting of the given character types.

    :param length: the length of the password.
    :param numeric: true, if numeric number shall be used, otherwise false.
    :param special_chars: the special characters, which shall be used.
    :return: the generated password.
    """
    if length <= 0:
        return ''
    else:
        char_set = string.ascii_letters + special_chars
        if numeric:
            char_set += string.digits
        return generate_password(length - 1, numeric, special_chars) + random.SystemRandom().choice(char_set)


if __name__ == '__main__':
    with open(settings.CONF_FILE, 'r+', encoding='utf-8') as fp:
        ccshuffle_conf = json.load(fp=fp)
        ccshuffle_conf['SECRET_KEY'] = generate_password(length=60,
                                                         special_chars='-.!#$%&(){}[]*+/:;<=>?@\^_|~')
        fp.seek(0)
        fp.truncate()
        json.dump(ccshuffle_conf, fp)
