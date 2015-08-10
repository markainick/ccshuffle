/**
 * Javascript for the crawling dashboard
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 is recommended.
 *
 * @version 0.1
 */

function Dashboard() {

    this.django_ajax = new DjangoAjax();
    this.ajax_request_url = '/crawler/';

    /**
     * Initializes the dashboard.
     */
    this.init = function () {
        this.django_ajax.setup()
    };

    /**
     * Starts the crawling process for the jamendo service.
     */
    this.crawl_jamendo = function () {
        $.ajax({
            type: 'GET',
            url: this.ajax_request_url,
            data: {
                'command': 'start-jamendo-crawl'
            },
            success: function (data) {
                console.log(data)
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log('An error (' + errorThrown + ') occurred for the \'start jamendo crawling\' request !');
            }
        });
    };
}

$(document).ready(function () {
    console.log('Welcome to the crawling dashboard of ccshuffle :)')

    var dashboard = new Dashboard();
    // Init dashboard
    dashboard.init();

    $('#start-jamendo-crawling').click(function () {
        console.log('User wants to start the jamendo crawling process.');
        dashboard.crawl_jamendo();
    });
});