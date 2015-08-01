__author__ = 'Kevin Haller'

import time
import unittest
from selenium import webdriver

# COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
#
#

django_url = 'http://localhost:8000'


class LoginTest(unittest.TestCase):
    """
        This class tests the login behaviour.
    """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_login_expected_way(self):
        """
            This test case tests the login behaviour, when the correct credentials are entered.
        """
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
        username_input.send_keys('amelie')
        password_input.send_keys('amelie')
        login_button.submit()
        # Amelie has logged in successfully and sees her username in the upper left corner.
        dropdown_user_menu = self.browser.find_element_by_id('dropdownUserMenu')
        self.assertEqual(dropdown_user_menu.text, 'amelie')

    def test_login_expected_way_mobil(self):
        """
            The test case tests the login behaviour on mobile devices, when the correct credentials are entered.
        """
        self.fail("Not implemented")

    def test_login_wrong_credentials(self):
        """
            The test case tests the login behaviour, when the wrong credentials are entered.
        """
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
        username_input.send_keys('amelie')
        password_input.send_keys('AMELIE')
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
            username_input.send_keys('amelie')
        password_input.send_keys('AMELIE')
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
            username_input.send_keys('amelie')
        password_input.send_keys('amelie')
        login_button.submit()
        # The login attempt succeeds and Amelie is redirected to the homepage, where her username is displayed in the
        # upper left corner.
        dropdown_user_menu = self.browser.find_element_by_id('dropdownUserMenu')
        self.assertIsNotNone(dropdown_user_menu)
        self.assertEqual(dropdown_user_menu.text, 'amelie')


class RegistrationTest(unittest.TestCase):
    """
        This class tests the registration behaviour.
    """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_registration(self):
        """
            This test case tests the registration process.
        """
        username = 'amelie@testing'
        password = 'the_cake_is_a_lie'
        email = 'amelie@gmail.com'
        # Amelie visits the homepage of the service and has no account, so she wants to register.
        # So she clicks on the 'register' button.
        self.browser.get(django_url)
        self.assertIn('Creative Commons Shuffle', self.browser.title)
        register_link = self.browser.find_element_by_id('link_register')
        register_link.click()
        # Now Amelie sees the registration page.
        self.assertIn('Register', self.browser.title)
        register_form = self.browser.find_element_by_id('register-form')
        username_input = register_form.find_element_by_id('id_username')
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
        username_input.send_keys(username)
        password1_input.send_keys(password)
        password2_input.send_keys(password)
        email_input.send_keys(email)
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
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.submit()
        # The login attempt succeeds and Amelie is redirected to the homepage, where her username is displayed in the
        # upper left corner.
        dropdown_user_menu = self.browser.find_element_by_id('dropdownUserMenu')
        self.assertIsNotNone(dropdown_user_menu)
        self.assertEqual(dropdown_user_menu.text, username)
        self.fail("Not implemented")


if __name__ == "main":
    unittest.main()
