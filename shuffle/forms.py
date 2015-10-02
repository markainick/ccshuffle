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

import re
from django import forms
from captcha.fields import ReCaptchaField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm)
from ccshuffle import in_functional_testing_mode


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Username'), 'required': 'required'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Password'), 'required': 'required'})


class RegistrationForm(UserCreationForm):
    password_pattern_str = r'.{6,}'
    username_pattern_str = r'^[\w.@+-]+$'

    email = forms.EmailField(label=_("Email"), max_length=2048, required=False, widget=forms.EmailInput)
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # If in functional testing mode, remove reCaptcha from the fields of the registration form.
        if in_functional_testing_mode():
            del self.fields['captcha']
        # Compile the pattern.
        self.password_pattern = re.compile(self.password_pattern_str)
        # Adds additional error messages.
        self.error_messages['password_pattern'] = _('The password must be at least 6 characters long.')
        self.error_messages['unique_username'] = _("A user with that username already exists.")
        # Designs the fields.
        self.design_fields()

    def design_fields(self):
        """ Designs the fields of the user creation form using bootstrap classes and HTML5. """
        self.fields['username'].widget.attrs.update({'id': 'id_username_register',
                                                     'class': 'form-control',
                                                     'placeholder': _('Username'),
                                                     'pattern': self.username_pattern_str,
                                                     'aria-describedby': 'basic-username',
                                                     'required': 'required'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': _('Password'),
                                                      'pattern': self.password_pattern_str,
                                                      'aria-describedby': 'basic-password',
                                                      'required': 'required'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control',
                                                      'placeholder': _('Password'),
                                                      'pattern': self.password_pattern_str,
                                                      'aria-describedby': 'basic-password-confirm',
                                                      'required': 'required'})
        self.fields['email'].widget.attrs.update({'class': 'form-control',
                                                  'placeholder': _('Your email'),
                                                  'aria-describedby': 'basic-email'})

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if not self.password_pattern.match(password1):
            raise forms.ValidationError(self.error_messages['password_pattern'], code='password_pattern_mismatch', )
        return password1

    def clean_password2(self):
        password2 = super(type(self), self).clean_password2()
        if not self.password_pattern.match(password2):
            raise forms.ValidationError(self.error_messages['password_pattern'], code='password_pattern_mismatch', )
        return password2

    def clean_email(self):
        return self.cleaned_data.get("email")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.clean_email()
        if commit:
            user.save()
        return user
