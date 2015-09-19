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

from django.conf.urls import url
from .views import (AboutPageView, IndexPageView, RegisterPageView,
                    NotFoundErrorPageView, SignInPageView, SignOutPageView)

urlpatterns = [
    url(r'^$', IndexPageView.as_view(), name="home"),
    url(r'register/$', RegisterPageView.as_view(), name="register"),
    url(r'login/$', SignInPageView.as_view(), name="signin"),
    url(r'logout/$', SignOutPageView.as_view(), name="signout"),
    url(r'about/$', AboutPageView.as_view(), name="about"),
    url(r'.*$', NotFoundErrorPageView.as_view(), name="404"),
]
