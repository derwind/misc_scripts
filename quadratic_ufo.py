#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re
from defcon import Font
from cu2qu.ufo import fonts_to_quadratic

def main():
    paths = [re.sub(r"{}+$".format(os.sep), "", path) for path in sys.argv[1:]]
    fonts = [Font(path) for path in paths]

    modified = fonts_to_quadratic(fonts, reverse_direction=True)

    print modified
    if modified:
        for path, font in zip(paths, fonts):
            basename, _ = os.path.splitext(os.path.basename(path))
            dirname = os.path.dirname(path)
            output_path = os.path.join(dirname, "{}_qcurve.ufo".format(basename))
            font.save(output_path)

if __name__ == "__main__":
    main()
