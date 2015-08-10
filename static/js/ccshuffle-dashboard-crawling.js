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
    this.crawl_jamendo = function (success_cb, error_cb) {
        $.ajax({
            type: 'GET',
            url: this.ajax_request_url,
            data: {
                'command': 'start-jamendo-crawl'
            },
            success: success_cb,
            error: error_cb
        });
    };
}

$(document).ready(function () {
    console.log('Welcome to the crawling dashboard of ccshuffle :)')

    var dashboard = new Dashboard();
    // Init dashboard
    dashboard.init();

    // Click handler for the start-jamendo-crawling button.
    $('#start-jamendo-crawling').click(function () {
        $(this).attr('disabled', 'disabled');
        dashboard.crawl_jamendo(function (data) {
            console.log(data);
            $(this).removeAttr('disabled');
        }, function (jqXHR, textStatus, errorThrown) {
            console.log('An error (' + errorThrown + ') occurred for the \'start jamendo crawling\' request !');
            $(this).removeAttr('disabled');
        });
    });
    // If the jamendo collapse link is clicked, flip the icon and change the text.
    /*$(document).on('shown.bs.collapse', function () {
     console.log('Link table collapse !');
     $(this).removeClass('not-collapsed');
     $(this).addClass('already-collapsed');
     });
     $(document).on('hide.bs.collapse', function () {
     console.log('Hide table collapse !');
     $(this).removeClass('already-collapsed');
     $(this).addClass('not-collapsed');
     });*/
});