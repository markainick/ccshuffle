#!/bin/sh

# You have to install the less compiler to run this command.
# Linux: http://stackoverflow.com/questions/7245826/less-compiler-for-linux

lessc 'ccshuffle.less' > '../css/ccshuffle.css'
lessc 'ccshuffle-about.less' > '../css/ccshuffle-about.css'