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

import time
import copy
import urllib
import unittest
from selenium import webdriver

django_url = 'http://localhost:8000'

amelie_username = 'amelie@testing'
amelie_password = 'the_cake_is_a_lie'
amelie_email = 'amelie@gmail.com'


class LoginTest(unittest.TestCase):
    """ This class tests the login behaviour. """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_login_expected_way(self):
        """ This test case tests the login behaviour, when the correct credentials are entered. """
        # Amelie visits the homepage of this service and she has already an account. On the upper side (in the header)
        # she sees the login box with the username and the password textfield, because she is working on a laptop.
        self.browser.get(django_url)
        self.assertIn('Creative Commons Shuffle', self.browser.title)
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # She entered here username and password correctly and presses the 'Login' - button besides the text fields.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # Amelie has logged in successfully and sees her username in the upper left corner.
        user_profile_link = self.browser.find_element_by_id('user-profile-link')
        self.assertEqual(user_profile_link.text, amelie_username)

    def test_login_expected_way_mobil(self):
        """ The test case tests the login behaviour on mobile devices, when the correct credentials are entered. """
        browser = copy.copy(self.browser)
        # Amelie visits the homepage of this service with her mobil phone, because she is on the way to go jogging and
        # so she has the laptop not with her. She want to listen to a paylist, which she created three days before.
        browser.set_window_size(500, 750)
        browser.get(django_url)
        # She sees the sign in button on the upper right corner and clicks it. She is redirected to the login page.
        login_link = browser.find_element_by_id('btn_login_xs')
        login_link.click()
        self.assertIn('Login', browser.title)
        login_button = browser.find_element_by_id('btn_login')
        username_input = browser.find_element_by_id("id_username")
        password_input = browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # Amelie enter her credentials and clicks the login button.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # The login attempt succeeds and Amelie is redirected to the homepage, where her username is displayed in the
        # navigation bar (which is shown, if the user clicks the menu button).
        navigation_bar_btn = browser.find_element_by_class_name('navbar-toggle')
        navigation_bar_btn.click()
        user_profile_link = browser.find_element_by_id('user-profile-link')
        self.assertIsNotNone(user_profile_link)
        self.assertEqual(user_profile_link.text, amelie_username)

    def test_login_wrong_credentials(self):
        """ The test case tests the login behaviour, when the wrong credentials are entered. """
        # Amelie visits the homepage of this service and she has already an account. On the upper side (in the header)
        # she sees the login box with the username and the password textfield, because she is working on a laptop.
        self.browser.get(django_url)
        self.assertIn('Creative Commons Shuffle', self.browser.title)
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # She entered here username and password not correctly and presses the 'Login' - button besides the text fields.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password.upper())  # wrong password
        login_button.submit()
        # Amelie is redirected to the login page, where a error message is displayed. This error message informs Amelie
        # about the unsuccessful login attempt.
        self.assertIn('Login', self.browser.title)
        error_message = self.browser.find_element_by_id('login-error-notification')
        self.assertIsNotNone(error_message, "An error message must be displayed")
        self.assertIn("Please enter a correct username and password. Note that both fields may be case-sensitive.",
                      error_message.text)
        # Amelie sees the login form above the error message.
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # Amelie thinks and enters her credentials again.
        if len(username_input.get_attribute('value')) == 0:
            print("The browser (%s) has not saved the entered username !" % self.browser.name)
            username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password.upper())
        login_button.submit()
        # The credentials are wrong again. An error message informs Amelie about the unsuccessful login attempt.
        # The login page is displayed again.
        self.assertIn('Login', self.browser.title)
        error_message = self.browser.find_element_by_id('login-error-notification')
        self.assertIsNotNone(error_message, "An error message must be displayed")
        self.assertIn("Please enter a correct username and password. Note that both fields may be case-sensitive.",
                      error_message.text)
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # Amelie wonders, what I'm doing wrong ? She notices that caps-lock was activated. She enters the credentials
        # again.
        if len(username_input.get_attribute('value')) == 0:
            print("The browser (%s) has not saved the entered username !" % self.browser.name)
            username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # The login attempt succeeds and Amelie is redirected to the homepage, where her username is displayed in the
        # upper left corner.
        user_profile_link = self.browser.find_element_by_id('user-profile-link')
        self.assertIsNotNone(user_profile_link)
        self.assertEqual(user_profile_link.text, amelie_username)

    def test_global_login_redirect(self):
        """
        Tests, if the user is redirected to the page, where she or he has been before, if she or he signed in to the
        service with the global login box.
        """
        # Amelie visits the homepage and searches for songs, which can be described with the tags
        # 'indie rock alternative'. Then she clicks on the search button.
        self.browser.get(django_url)
        search_phrase_textfield = self.browser.find_element_by_name('search_phrase')
        search_phrase_textfield.send_keys('indie alternative rock')
        search_button = self.browser.find_element_by_id('start-search-button')
        search_button.click()
        # Amelie gets the search result for her search terms and now wants to login, because she found a song at the
        # top of the search result, which she wants to favorite (after listening).
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # Amelie enters her credentials into the login area on the upper right corner.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # The login attempt was successful and Amelie is redirected back to the search result.
        redirect_link_parsed = urllib.parse.urlparse(self.browser.current_url)
        redirect_link_params = urllib.parse.parse_qs(redirect_link_parsed.query, strict_parsing=False)
        self.assertIn('search_phrase', redirect_link_params,
                      'The url must contains the search phrase, so that Amelie gets the same search result')
        self.assertIn('indie', redirect_link_params['search_phrase'][0])
        self.assertIn('rock', redirect_link_params['search_phrase'][0])
        self.assertIn('alternative', redirect_link_params['search_phrase'][0])

    def test_login_mobil_redirect(self):
        """
        Tests, if the user is redirected to the page, where she or he has been before, if she or he clicks on the
        login button and sign in on the separate login page.
        """
        browser = copy.copy(self.browser)
        browser.get(django_url)
        browser.set_window_size(500, 750)
        # Amelie feels a little bit bored and she visits this service to maybe explore new music in her favorite genre
        # and searches for 'alternative indie rock'.
        search_phrase_textfield = browser.find_element_by_name('search_phrase')
        search_phrase_textfield.send_keys('indie alternative rock')
        search_button = browser.find_element_by_id('start-search-button')
        search_button.click()
        # Amelie gets the search result for her search terms and now wants to login, because she found a song at the
        # top of the search result, which she wants to favorite (after listening).
        login_link = browser.find_element_by_id('btn_login_xs')
        login_link.click()
        self.assertIn('Login', browser.title)
        login_button = browser.find_element_by_id('btn_login')
        username_input = browser.find_element_by_id("id_username")
        password_input = browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # The login attempt was successful and Amelie is redirected back to the search result.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # The login attempt was successful and Amelie is redirected back to the search result.
        redirect_link_parsed = urllib.parse.urlparse(self.browser.current_url)
        redirect_link_params = urllib.parse.parse_qs(redirect_link_parsed.query, strict_parsing=False)
        self.assertIn('search_phrase', redirect_link_params,
                      'The url must contains the search phrase, so that Amelie gets the same search result')
        self.assertIn('indie', redirect_link_params['search_phrase'][0])
        self.assertIn('rock', redirect_link_params['search_phrase'][0])
        self.assertIn('alternative', redirect_link_params['search_phrase'][0])


class RegistrationTest(unittest.TestCase):
    """ This class tests the registration behaviour. """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_registration(self):
        """
            This test case tests the registration process.
        """
        # Amelie visits the homepage of the service and has no account, so she wants to register.
        # So she clicks on the 'register' button.
        self.browser.get(django_url)
        self.assertIn('Creative Commons Shuffle', self.browser.title)
        register_link = self.browser.find_element_by_id('link_register')
        register_link.click()
        # Now Amelie sees the registration page.
        self.assertIn('Register', self.browser.title)
        register_form = self.browser.find_element_by_id('register-form')
        username_input = register_form.find_element_by_id('id_username_register')
        password1_input = register_form.find_element_by_id('id_password1')
        password2_input = register_form.find_element_by_id('id_password2')
        self.assertEqual(username_input.get_attribute('placeholder'), 'Username',
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual(password1_input.get_attribute('placeholder'), 'Password',
                         "The placeholder text of the first password field must be 'Password' ")
        self.assertEqual(password2_input.get_attribute('placeholder'), 'Password',
                         "The placeholder text of the second password field must be 'Password' ")
        email_input = self.browser.find_element_by_id('id_email')
        create_account_button = self.browser.find_element_by_id('btn_create_account')
        # She enters the username 'amelie@testing' as well as the desired password. She also enters the email to ensure,
        # that she has the option to reset the password. Amelie is aware of forgetting the password.
        username_input.send_keys(amelie_username + '#2')
        password1_input.send_keys(amelie_password)
        password2_input.send_keys(amelie_password)
        email_input.send_keys(amelie_email)
        # Afterwards Amelie clicks on the 'create account'-button.
        create_account_button.click()
        # The registration was successful and Amelie is redirected to the login page, where a message is displayed to
        # inform Amelie about the successful registration and that now the login is possible.
        self.assertIn('Login', self.browser.title, 'The user must be redirected to the login page')
        registration_success_message = self.browser.find_element_by_class_name('alert')
        self.assertIn(registration_success_message, "The registration was successful.")
        # Amelie enters her credentials.
        login_button = self.browser.find_element_by_id('btn_login')
        username_input = self.browser.find_element_by_id("id_username")
        password_input = self.browser.find_element_by_id("id_password")
        self.assertEqual('Username', username_input.get_attribute('placeholder'),
                         "The placeholder text of the username field must be 'Username' ")
        self.assertEqual('Password', password_input.get_attribute('placeholder'),
                         "The placeholder text of the password field must be 'Password' ")
        # She entered here username and password not correctly and presses the 'Login' - button besides the text fields.
        username_input.send_keys(amelie_username)
        password_input.send_keys(amelie_password)
        login_button.submit()
        # The login attempt succeeds and Amelie is redirected to the homepage, where her username is displayed in the
        # upper left corner.
        user_profile_link = self.browser.find_element_by_id('user-profile-link')
        self.assertIsNotNone(user_profile_link)
        self.assertEqual(user_profile_link.text, amelie_username + '#2')
        self.fail("Not implemented")


if __name__ == "__main__":
    unittest.main()
