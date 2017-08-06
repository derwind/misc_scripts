#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

def main():
    glyphs_f = sys.argv[1]

    with open(glyphs_f) as f:
        indent = 0
        postponed_indent = 0
        for line in f.readlines():
            indent += postponed_indent
            postponed_indent = 0

            line = line.rstrip()

            # remove string and calculate indent
            shrinked_line = re.sub(r'".*"', "", line)
            if re.search(r"{\s*$", shrinked_line) or re.search(r"\(\s*$", shrinked_line):
                postponed_indent += 2
            if re.search(r"}", shrinked_line) or re.search(r"\)", shrinked_line):
                indent -= 2

            if indent < 0:
                raise Exception("invalid indent!")

            print " "*indent + line

if __name__ == "__main__":
    main()
