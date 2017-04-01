#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from robofab.world import OpenFont
from fontTools.agl import AGL2UV

if __name__ == "__main__":
    path = sys.argv[1]
    path = re.sub("{}+$".format(os.sep), "", path)
    basename, _ = os.path.splitext(os.path.basename(path))
    dirname = os.path.dirname(path)
    output_ufo = os.path.join(dirname, "{}_with_unicodes.ufo".format(basename))

    font = OpenFont(path)
    for g in font:
        if not g.unicodes and g.name in AGL2UV:
            g.unicode = AGL2UV[g.name]
    font.save(output_ufo)
