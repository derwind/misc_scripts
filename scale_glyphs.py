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
        self.font = None
        self._scale = scale
        self.isCID = True

    def run(self):
        self.font = TTFont(self.in_font)
        self.update_cff()
        self.update_head()
        self.update_hmtx()
        self.update_vmtx()
        self.font.save(self.out_font)

    def update_cff(self):
        cff = self.font["CFF "].cff
        topDict = cff.topDictIndex[0]
        self.isCID = hasattr(topDict, "FDArray")

        gs = self.font.getGlyphSet()
        order = self.font.getGlyphOrder()

        self.update_glyps_widths(gs, topDict)
        self.update_default_and_nominal_width(topDict)

    def update_glyps_widths(self, gs, topDict):
        globalSubrs = topDict.GlobalSubrs
        charStrings = topDict.CharStrings

        for name in gs.keys():
            g = gs[name]
            c, fdSelectIndex = topDict.CharStrings.getItemAndSelector(name)
            if self.isCID:
                private = topDict.FDArray[fdSelectIndex].Private
            else:
                private = topDict.Private

            dfltWdX = private.defaultWidthX
            nmnlWdX = private.nominalWidthX

            width = g.width - nmnlWdX

            transformation = (self._scale, 0, 0, self._scale, 0, 0)
            t2Pen = T2CharStringPen(width, gs)
            transPen = TransformPen(t2Pen, transformation)
            g.draw(transPen)
            charString = t2Pen.getCharString(private, globalSubrs)
            glyphID = charStrings.charStrings[name]

            self.update_glyph_width(charString, nmnlWdX)
            charStrings.charStringsIndex.items[glyphID] = charString

    def update_glyph_width(self, charString, nmnlWdX):
        int_args = []
        for b in charString.program:
            if isinstance(b, int):
                int_args.append(b)
            elif isinstance(b, str):
                if b == "rmoveto":
                    if len(int_args) != 2:
                        break
                elif b == "hmoveto" or b == "vmoveto":
                    if len(int_args) != 1:
                        break
                elif b == "endchar":
                    if len(int_args) != 0:
                        break
                else:
                    return
        charString.program[0] = self.scale(charString.program[0])

    def update_default_and_nominal_width(self, topDict):
        if self.isCID:
            for fd in topDict.FDArray:
                private = fd.Private
                private.defaultWidthX = self.scale(private.defaultWidthX)
                private.nominalWidthX = self.scale(private.nominalWidthX)
        else:
            private = topDict.Private
            private.defaultWidthX = self.scale(private.defaultWidthX)
            private.nominalWidthX = self.scale(private.nominalWidthX)

    def update_head(self):
        head = self.font["head"]
        head.unitsPerEm = self.scale(head.unitsPerEm)
        head.xMin = self.scale(head.xMin)
        head.yMin = self.scale(head.yMin)
        head.xMax = self.scale(head.xMax)
        head.yMax = self.scale(head.yMax)

    def update_hmtx(self):
        hmtx = self.font["hmtx"]
        for gname in hmtx.metrics.keys():
            adw, lsb = hmtx.metrics[gname]
            hmtx.metrics[gname] = (self.scale(adw), self.scale(lsb))

    def update_vmtx(self):
        if "vmtx" not in self.font:
            return

        vmtx = self.font["vmtx"]
        for gname in vmtx.metrics.keys():
            adh, tsb = vmtx.metrics[gname]
            vmtx.metrics[gname] = (self.scale(adh), self.scale(tsb))

    def scale(self, value):
        return int(value * self._scale)

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
