/**
 * Javascript for django ajax.
 * COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 * Licensed under the GPLv3 license
 *
 * To use this javascript library jquery >= 2.1.4 is recommended.
 *
 * @version 0.2
 */

/**
 * Returns true if the given HTTP method does not need csrf protection, otherwise false.
 *
 * @param method    the method, which shall be checked.
 * @returns {boolean} true, if the given HTTP method does not need csrf protection, otherwise false.
 */
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function DjangoAjax() {
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
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", this.csrftoken);
                }
            }
        });
    };

    /**
     * Sends a GET request to the given url with the given data.
     *
     * @param url the url, to which the request shall be send.
     * @param data the data, which shall be send.
     * @param callback a function, which is called, if the response has been received. The first and only parameter
     * passes the response project.
     */
    this.requestGet = function (url, data, callback) {
        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                callback(ResponseObject.fromJson(data));
            },
            error: function (jqXHR, textStatus, errorThrown) {
                callback(new ResponseObject('fail', errorThrown, null));
            }
        });
    };

    /**
     * Sends a POST request to the given url with the given data.
     *
     * @param url the url, to which the request shall be send.
     * @param data the data, which shall be send.
     * @param callback a function, which is called, if the response has been received. The first and only parameter
     * passes the response project.
     */
    this.requestPost = function (url, data, callback) {
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                callback(ResponseObject.fromJson(data));
            },
            error: function (jqXHR, textStatus, errorThrown) {
                callback(new ResponseObject('fail', errorThrown, null));
            }
        });
    };
}

/**
 * This class represents a response object which has been received after a ajax request.
 *
 * @param status the status of the response.
 * @param errorMessage the error message of the response, if the request (which caused this response) failed.
 * @param result the result of the response.
 * @constructor returns a new response object.
 */
function ResponseObject(status, errorMessage, result) {

    var ResponseStatus = {
        'fail': 0,
        'success': 1
    };

    this.status = ResponseStatus[status];
    this.errorMessage = errorMessage;
    this.result = result;

    /**
     * Checks, if this response obejct indicates a fail.
     *
     * @returns {boolean} true, if the request (which caused this response) failed, otherwise false.
     */
    this.failed = function () {
        return !Boolean(status);
    };

    /**
     * Checks, if this response object indicates a success.
     *
     * @returns {boolean}  true, if the request (which caused this response) succeeded, otherwise false.
     */
    this.succeeded = function () {
        return Boolean(status);
    };
}

/**
 * Parses the given json string and returns the corresponding response object.
 *
 * @param responseObjectJson the json string of the response object, which shall be parsed.
 * @returns {ResponseObject} the parsed response object.
 */
ResponseObject.fromJson = function (responseObjectJson) {
    if (responseObjectJson.hasOwnProperty('header') && responseObjectJson.hasOwnProperty('result')) {
        if (responseObjectJson['header'].hasOwnProperty('status') && (responseObjectJson['header']['status'] == 'fail' || responseObjectJson['header']['status'] == 'success')) {
            return new ResponseObject(responseObjectJson['header']['status'],
                ('error_msg' in responseObjectJson['header']) ? responseObjectJson['header']['error_msg'] : null,
                responseObjectJson['result']);
        } else {
            return new ResponseObject('fail', 'The status of the response is unknown.', null);
        }
    } else {
        return new ResponseObject('fail', 'The response is corrupted. The header or result entry is missing.', null);
    }
};