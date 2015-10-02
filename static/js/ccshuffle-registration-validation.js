/**
 * Javascript for the crawling dashboard
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 and ccshuffle-django-ajax >= 0.1 is recommended.
 *
 * @version 0.2
 */

/**
 * This class represents a registration controller.
 *
 * @constructor a new registration controller.
 */
function RegistrationController() {

    this.django_ajax = new DjangoAjax();
    this.ajax_request_url = '/register/';

    /**
     * Initializes the registration controller.
     */
    this.init = function () {
        this.django_ajax.setup();
    };

    /**
     * Checks, if the given username is available.
     *
     * @param username the username, which shall be checked, if it is available.
     * @param callback a function of which the first and only parameter indicates the availability of the username.
     */
    this.isUsernameAvailable = function (username, callback) {
        this.django_ajax.requestGet(this.ajax_request_url + 'username-available', {'username': username},
            function (responseObject) {
                callback(responseObject.result);
            });
    };

    /**
     * Redesigns the given form to indicate that the entered text is valid.
     *
     * @param selector_form the selector of the form group, which shall be redesigned.
     */
    this.indicateValidFormInput = function (selector_form) {
        $(selector_form).removeClass('has-error');
        $(selector_form).removeClass('has-warning');
        $(selector_form).addClass('has-success');
    };

    /**
     * Redesigns the given form to indicate that the entered text is invalid.
     *
     * @param selector_form the selector of the form group, which shall be redesigned.
     */
    this.indicateInvalidFormInput = function (selector_form) {
        $(selector_form).removeClass('has-success');
        $(selector_form).removeClass('has-warning');
        $(selector_form).addClass('has-error');
    };

    /**
     * Redesigns the given form to indicate that the entered text is maybe invalid (warning).
     *
     * @param selector_form the selector of the form group, which shall be redesigned.
     */
    this.indicateWarningFormInput = function (selector_form) {
        $(selector_form).removeClass('has-success');
        $(selector_form).removeClass('has-error');
        $(selector_form).addClass('has-warning');
    };

    /**
     * Returns the given form group back to the original design.
     *
     * @param selector_form the selector of the form group, which shall be brought back to the original design.
     */
    this.removeFormInputIndication = function (selector_form) {
        $(selector_form).removeClass('has-success');
        $(selector_form).removeClass('has-warning');
        $(selector_form).removeClass('has-error');
    }
}

$(document).ready(function () {
    var registrationController = new RegistrationController();

    /** Initializes the registration controller */
    registrationController.init();

    /**
     * Checks, if the entered username of the username input field is valid and marks it accordingly. The username is
     * valid, if the username does not already exist. The username also must consist of alphanumeric characters or
     * the special characters .@+- .
     *
     * @param value the entered username of the username input field.
     */
    var usernameValidCheck = function (value, callback) {
        if (value) {
            registrationController.isUsernameAvailable(value, function (available) {
                if (!Modernizr.input.pattern || !Modernizr.formvalidation) {
                    available &= value.match(new RegExp($("#id_username_register").attr("pattern")));
                }
                if (Modernizr.formvalidation) {
                    available &= $("#id_username_register")[0].checkValidity();
                }
                callback(available);
            });
        }
    };

    /** On init, check the (maybe) already entered username */
    if ($("#id_username_register").val()) {
        usernameValidCheck($("#id_username_register").val(), function (available) {
            if (available) {
                registrationController.indicateValidFormInput("#username-register-form-group");
            } else {
                registrationController.indicateInvalidFormInput("#username-register-form-group");
            }
        });
    }

    /**
     * Checks, if the password of the first password input field is valid. The validity of the entered password of the
     * second password input field is checked for every change of the password of the first password input field.
     *
     * @param value the password of the second password input field.
     * @return {boolean} true, if the password of the first password input field is valid, otherwise false.
     */
    var password1ValidCheck = function (value) {
        var validity = true;
        if (!Modernizr.input.required || !Modernizr.formvalidation) {
            validity &= Boolean(value);
        }
        if (!Modernizr.input.pattern || !Modernizr.formvalidation) {
            validity &= (value.match(new RegExp($("#id_password1").attr("pattern"))) !== null);
        }
        if (Modernizr.formvalidation) {
            validity &= $("#id_password1")[0].checkValidity();
        }
        return validity;
    };

    /**
     *  Checks, if the password of the second password input field is valid. The password is valid, if it is equal to
     *  the entered password of the first password input field. It is always invalid, if the entered password of the
     *  first password field is invalid.
     *
     * @param value the password of the second password input field.
     * @return {boolean} true, if the password of the second password input field is valid, otherwise false.
     */
    var password2ValidCheck = function (value) {
        var password1 = $("#id_password1").val();
        return (value == password1) && password1ValidCheck(password1);
    };

    /**
     * Checks, if the entered email address is valid. If the email input type or the html5 form validation is not
     * supported by the current browser, a own email regex will be used. The email regex can be found here
     * http://emailregex.com/.
     *
     * @param value the email of the email input field.
     * @return {boolean} true, if the entered email is valid, otherwise false.
     */
    var emailValidCheck = function (value) {
        var validity = true;
        if (!Modernizr.inputtypes.email || !Modernizr.formvalidation) {
            validity &= (null !== value.match(new RegExp("^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$")));
        } else {
            validity &= $("#id_email")[0].checkValidity();
        }
        return validity;
    };

    /**
     * Adds the type change handler to the username input field of the registration form.
     */
    $("#id_username_register").typeWatch({
        callback: function (value) {
            usernameValidCheck(value, function (available) {
                if (available) {
                    registrationController.indicateValidFormInput("#username-register-form-group");
                } else {
                    registrationController.indicateInvalidFormInput("#username-register-form-group");
                }
            });
        },
        wait: 750,
        highlight: true,
        captureLength: 0
    });

    /**
     * Adds the type change handler to the first password input field of the registration form.
     */
    $("#id_password1").typeWatch({
        callback: function (value) {
            if (password1ValidCheck(value)) {
                registrationController.indicateValidFormInput("#password1-form-group");
            } else {
                registrationController.indicateInvalidFormInput("#password1-form-group");
            }
            password2ValidCheck($("#id_password2").val());
        },
        wait: 750,
        highlight: true,
        captureLength: 0
    });

    /**
     * Adds the type change handler to the second password input field of the registration form.
     */
    $("#id_password2").typeWatch({
        callback: function (value) {
            if (password2ValidCheck(value)) {
                registrationController.indicateValidFormInput("#password2-form-group");
            } else {
                registrationController.indicateInvalidFormInput("#password2-form-group");
            }
        },
        wait: 750,
        highlight: true,
        captureLength: 0
    });

    /**
     * Adds the type change handler to the email input field of the registration form.
     */
    $("#id_email").typeWatch({
        callback: function (value) {
            if (value) {
                if (emailValidCheck(value)) {
                    registrationController.indicateValidFormInput("#email-form-group");
                } else {
                    registrationController.indicateWarningFormInput("#email-form-group");
                }
            } else {
                registrationController.removeFormInputIndication("#email-form-group");
            }
        },
        wait: 750,
        highlight: true,
        captureLength: 0
    });
});
