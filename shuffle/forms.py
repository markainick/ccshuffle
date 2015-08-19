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

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm)


class LoginForm(AuthenticationForm):
    """ This form represents the login form. """

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username', 'required': 'required'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password', 'required': 'required'})


class RegistrationForm(UserCreationForm):
    """ This form represents the registration form. """

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['email'] = forms.EmailField(label=_("Email"), max_length=2048, required=False)

        self.fields['username'].widget.attrs.update({'id': 'id_username_register',
                                                     'class': 'form-control',
                                                     'placeholder': 'Username',
                                                     'aria-describedby': 'basic-username',
                                                     'required': 'required'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': 'Password',
                                                      'aria-describedby': 'basic-password',
                                                      'required': 'required'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': 'Password',
                                                      'aria-describedby': 'basic-password-confirm',
                                                      'required': 'required'})
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': 'Your email',
                                                  'aria-describedby': 'basic-email'})
