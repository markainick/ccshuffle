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

def get_jamendo_api_auth_code():
    """
    Returns the authentication code for using the jamendo api.

    :return: the authentication code for using the jamendo api.
    """
    if 'JAMENDO_AUTH' in os.environ:
        return os.environ['JAMENDO_AUTH']
    else:
        raise ValueError('The jamendo authentication code is not set. You can specify it in the CONF_FILE or by setting the environment variable \'JAMENDO_AUTH\'.')
