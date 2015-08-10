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
        $(this).prop("disabled", true);
        dashboard.crawl_jamendo(function (data) {
            console.log(data);
            var response = JSON.parse(data);
            if (response['header']['status'] === 'success') {
                addCrawlingProcessRow('#jamendo-cp-table', response['result']);
            } else {
                console.log(response['header']['error_message']);
            }
            $(this).prop("disabled", false); //TODO does not work
        }, function (jqXHR, textStatus, errorThrown) {
            console.log('An error (' + errorThrown + ') occurred for the \'start jamendo crawling\' request !');
            $(this).prop("disabled", false); //TODO does not work
        });
    });

    /**
     * Adds the crawling process information as row to the table given with the selector.
     *
     * @param selector the selector of the table.
     * @param cp_data the crawling process information received.
     */
    function addCrawlingProcessRow(selector, cp_data) {
        var execution_date = new Date(cp_data['execution_date'])
        $(selector + ' tbody').first().prepend('<tr>' +
            '<td>' + cp_data['service'] + '</td>' +
            '<td>' + jQuery.format.date(execution_date, 'E dd MM yyyy - HH:mm') + '</td>' +
            '<td>' + cp_data['status'] + '</td>' +
            '<td>' + cp_data['exception'] + '</td>' +
            '</tr>');
    }
});

