/**
 * Javascript for django ajax.
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 is recommended.
 *
 * @version 0.1
 */
function DjangoAjax() {

    /**
     * Returns true if the given HTTP method does not need csrf protection, otherwise false.
     *
     * @param method    the method, which shall be checked.
     * @returns {boolean} true, if the given HTTP method does not need csrf protection, otherwise false.
     */
    this.csrfSafeMethod = function (method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    /**
     * Gets the cookie with the given name.
     *
     * @param name the name of the cookie of which the value shall be read in.
     * @returns the values of the cookie with the given name.
     */
    this.getCookie = function (name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    this.csrftoken = this.getCookie('csrftoken');

    /**
     * Setups the ajax functionality for django. It adds a function that is executed before every send, which adds the
     * csrf token for post requests.
     */
    this.setup = function () {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (/*!this.csrfSafeMethod(settings.type) &&*/ !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", this.csrftoken);
                }
            }
        });
    };
}