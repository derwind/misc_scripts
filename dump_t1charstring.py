#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from fontTools.t1Lib import T1Font

def main():
    t1_font = T1Font(sys.argv[1])
    gs = t1_font.getGlyphSet()
    # charstrings = t1_font.font["CharStrings"]
    charstrings = t1_font["CharStrings"]
    for gname in gs:
        g = charstrings[gname]
        g.decompile()
        print("[{}]".format(gname))
        operands = []
        for b in g.program:
            if isinstance(b, int):
                operands.append(b)
            else:
                print("  [{}] << {} >>".format(", ".join(map(lambda v: str(v), operands)), b))
                operands = []
        print("  -----")

if __name__ == "__main__":
    main()
