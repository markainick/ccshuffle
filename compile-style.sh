#!/bin/sh

# Shell script for compiling the stylesheets.
#
# Requirements:
#   + lessc - You have to install the less compiler to run this command.
#             Linux: http://stackoverflow.com/questions/7245826/less-compiler-for-linux

# Compile the stylesheets
lessc 'static/less/ccshuffle.less' > 'static/css/ccshuffle.css'
lessc 'static/less/ccshuffle-about.less' > 'static/css/ccshuffle-about.css'
lessc 'static/less/ccshuffle-dashboard-crawling.less' > 'static/css/ccshuffle-dashboard-crawling.css'

