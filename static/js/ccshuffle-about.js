/**
 *  Javascript for the CCShuffle about page.
 *
 *  COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 */

$(document).ready(function () {
    console.log('Welcome to creative commons shuffle information page :)');

    // Make the navigation bar transparent, only if javascript is enabled.
    $('nav').addClass('navbar-transparent');

    /*
     * Script for smooth scrolling.
     *
     * http://www.learningjquery.com/2007/10/improved-animated-scrolling-script-for-same-page-links
     */
    $(function () {
        $('a[href*=#]:not([href=#])').click(function () {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: target.offset().top
                    }, 1000);
                    return false;
                }
            }
        });
    });

    // Registers the navigation bar for the bootstrap scroll spy plugin.
    $('body').scrollspy({
        target: '#navigation-bar',
        offset: 51
    });

    $('#navigation-bar').affix({
        offset: {
            top: 100
        }
    });
});