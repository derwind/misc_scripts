#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from fontTools.t1Lib import T1Font
from fontTools.pens.recordingPen import RecordingPen

def main():
    t1_font = T1Font(sys.argv[1])
    gs = t1_font.getGlyphSet()
    # charstrings = t1_font.font["CharStrings"]
    charstrings = t1_font["CharStrings"]
    for gname in gs:
        g = charstrings[gname]
        pen = RecordingPen()
        g.draw(pen)
        print "[{}]".format(gname)
        for operator, operands in pen.value:
            print operator, operands

if __name__ == "__main__":
    main()
