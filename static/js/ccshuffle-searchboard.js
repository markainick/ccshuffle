/**
 * Javascript for the searching board.
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 is recommended.
 */
$(document).ready(function () {

    console.log('Starting search control js.');

    /**
     * Adds a handler, which fires, if the search navigation bar activation changes, so that the value of the hidden
     * field search_for of the search-form changes too.
     */
    $(document).on('shown.bs.tab', 'a[data-toggle="tab"]', function (e) {
        $('#search-form input[name="search_for"]').attr('value', e.target.getAttribute('href').replace('#', ''))
    });

    /**
     * Adds a handler to the search field so that if the tab 'tags' is activated, the single keywords are
     * highlighted.
     */
    $('#search-form input[name="search_phrase"]').on('input', function () {
        console.log('Change');
    });

});