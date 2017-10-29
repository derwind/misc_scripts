#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

def main():
    font_path = sys.argv[1]
    scale = 2.048
    if len(sys.argv) > 2:
        scale = float(sys.argv[2])

    font = TTFont(font_path)
    cff = font["CFF "].cff
    charStrings = cff.topDictIndex[0].CharStrings
    gs = font.getGlyphSet()

    for name in gs.keys():
        g = gs[name]

        transformation = (scale, 0, 0, scale, 0, 0)
        t2Pen = T2CharStringPen(g.width, gs)
        transPen = TransformPen(t2Pen, transformation)
        g.draw(transPen)
        charStrings[name] = t2Pen.getCharString()

    font.save("out.otf")

if __name__ == "__main__":
    main()
