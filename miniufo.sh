#! /bin/sh

tx -ufo -g `ruby -e 'print [".notdef","space",*"A".."Z",*"a".."z"].join(",")'` -o font.shrinked.ufo font.ufo
