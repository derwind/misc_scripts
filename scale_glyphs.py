#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
import argparse
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

class GlyphsScaler(object):
    def __init__(self, in_font, out_font, scale=2.048):
        self.in_font = in_font
        self.out_font = out_font
        self.scale = scale

    def run(self):
        font = TTFont(self.in_font)
        cff = font["CFF "].cff
        topDict = cff.topDictIndex[0]
        globalSubrs = topDict.GlobalSubrs
        charStrings = topDict.CharStrings
        gs = font.getGlyphSet()
        order = font.getGlyphOrder()

        isCID = hasattr(topDict, "FDArray")

        for name in order:
            g = gs[name]
            c, fdSelectIndex = topDict.CharStrings.getItemAndSelector(name)
            if isCID:
                private = topDict.FDArray[fdSelectIndex].Private
            else:
                private = topDict.Private

            dfltWdX = private.defaultWidthX
            nmnlWdX = private.nominalWidthX

            width = g.width
            width = width - nmnlWdX

            transformation = (self.scale, 0, 0, self.scale, 0, 0)
            t2Pen = T2CharStringPen(width, gs)
            transPen = TransformPen(t2Pen, transformation)
            g.draw(transPen)
            charString = t2Pen.getCharString(private, globalSubrs)
            glyphID = charStrings.charStrings[name]
            charStrings.charStringsIndex.items[glyphID] = charString

            g.width = int(g.width * self.scale)

        font.save("out.otf")

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_font", metavar="FONT", type=str,
                        help="FONT")
    parser.add_argument("-o", "--output", dest="out_font", default=None,
                        help="output font")
    parser.add_argument("-s", "--scale", dest="scale", default=None,
                        help="scale")

    args = parser.parse_args()

    if args.out_font is None:
        args.out_font = args.in_font

    return args

def main():
    args = get_args()

    scale = 2.048
    if args.scale:
        scale = float(args.scale)

    scaler = GlyphsScaler(args.in_font, args.out_font, scale)
    scaler.run()

if __name__ == "__main__":
    main()
