#! /bin/sh

TEXT="ABCDE"

hb-view --output-format=png --output-file=result.png --text=$TEXT --features="salt=3" --font-file=test.otf
