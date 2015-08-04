/**
 * Javascript for the crawling dashboard
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 is recommended.
 */
$(document).ready(function () {
    console.log('Welcome to the crawling dashboard of ccshuffle :)')
    /**
     * Returns true if the given HTTP method does not need csrf protection, otherwise false.
     * @param method    the method, which shall be checked.
     * @returns {boolean} true, if the given HTTP method does not need csrf protection, otherwise false.
     */
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    /**
     *
     * @param name
     * @returns {*}
     */
    function getCookie(name) {
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
    }

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    /**
     * Starts the crawling process for the jamendo service.
     */
    function start_jamendo_crawling() {
        $.ajax({
            type: 'GET',
            url: '/crawler/',
            data: {
                'command': 'start-jamendo-crawl'
            },
            success: function (data) {
                console.log(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log('An error (' + errorThrown + ') occurred for the \'start jamendo crawling\' request !')
            }
        });
    }

    $('#start-jamendo-crawling').click(function () {
        console.log('User wants to start the jamendo crawling process.');
        start_jamendo_crawling();
    });
});