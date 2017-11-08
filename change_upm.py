#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
change units per EM
"""

import os, sys, re
import argparse
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

class GlyphsScaler(object):
    def __init__(self, in_font, out_font, upm=2048):
        self.in_font = in_font
        self.out_font = out_font
        self.font = TTFont(self.in_font)
        self._scale = round(1. * upm / self.font["head"].unitsPerEm, 3)
        self.isCID = True

    def run(self):
        self.update_BASE()
        self.update_CFF()
        self.update_GPOS()
        self.update_OS_2()
        self.update_VORG()
        self.update_head()
        self.update_hhea()
        self.update_hmtx()
        self.update_post()
        self.update_vhea()
        self.update_vmtx()
        self.font.save(self.out_font)

    def update_BASE(self):
        base = self.font["BASE"]
        for record in base.table.HorizAxis.BaseScriptList.BaseScriptRecord:
            for coord in record.BaseScript.BaseValues.BaseCoord:
                coord.Coordinate = self.scale(coord.Coordinate)
        for record in base.table.VertAxis.BaseScriptList.BaseScriptRecord:
            for coord in record.BaseScript.BaseValues.BaseCoord:
                coord.Coordinate = self.scale(coord.Coordinate)

    def update_CFF(self):
        cff = self.font["CFF "].cff
        topDict = cff.topDictIndex[0]
        self.isCID = hasattr(topDict, "FDArray")

        topDict.UnderlinePosition = self.scale(topDict.UnderlinePosition)
        topDict.UnderlineThickness = self.scale(topDict.UnderlineThickness)
        topDict.FontBBox = map(lambda v: self.scale(v), topDict.FontBBox)
        topDict.StrokeWidth = self.scale(topDict.StrokeWidth)

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

    def update_GPOS(self):
        pass

    def update_OS_2(self):
        os_2 = self.font["OS/2"]
        os_2.xAvgCharWidth = self.scale(os_2.xAvgCharWidth)
        os_2.ySubscriptXSize = self.scale(os_2.ySubscriptXSize)
        os_2.ySubscriptYSize = self.scale(os_2.ySubscriptYSize)
        os_2.ySubscriptXOffset = self.scale(os_2.ySubscriptXOffset)
        os_2.ySubscriptYOffset = self.scale(os_2.ySubscriptYOffset)
        os_2.ySuperscriptXSize = self.scale(os_2.ySuperscriptXSize)
        os_2.ySuperscriptYSize = self.scale(os_2.ySuperscriptYSize)
        os_2.ySuperscriptXOffset = self.scale(os_2.ySuperscriptXOffset)
        os_2.ySuperscriptYOffset = self.scale(os_2.ySuperscriptYOffset)
        os_2.yStrikeoutSize = self.scale(os_2.yStrikeoutSize)
        os_2.yStrikeoutPosition = self.scale(os_2.yStrikeoutPosition)
        os_2.sTypoAscender = self.scale(os_2.sTypoAscender)
        os_2.sTypoDescender = self.scale(os_2.sTypoDescender)
        os_2.sTypoLineGap = self.scale(os_2.sTypoLineGap)
        os_2.usWinAscent = self.scale(os_2.usWinAscent)
        os_2.usWinDescent = self.scale(os_2.usWinDescent)
        os_2.sxHeight = self.scale(os_2.sxHeight)
        os_2.sCapHeight = self.scale(os_2.sCapHeight)

    def update_VORG(self):
        if "VORG" not in self.font:
            return

        vorg = self.font["VORG"]
        for name in vorg.VOriginRecords.keys():
            vorg.VOriginRecords[name] = self.scale(vorg.VOriginRecords[name])
        vorg.defaultVertOriginY = self.scale(vorg.defaultVertOriginY)

    def update_head(self):
        head = self.font["head"]
        head.unitsPerEm = self.scale(head.unitsPerEm)
        head.xMin = self.scale(head.xMin)
        head.yMin = self.scale(head.yMin)
        head.xMax = self.scale(head.xMax)
        head.yMax = self.scale(head.yMax)

    def update_hhea(self):
        hhea = self.font["hhea"]
        hhea.ascent = self.scale(hhea.ascent)
        hhea.descent = self.scale(hhea.descent)
        hhea.lineGap = self.scale(hhea.lineGap)
        hhea.advanceWidthMax = self.scale(hhea.advanceWidthMax)
        hhea.minLeftSideBearing = self.scale(hhea.minLeftSideBearing)
        hhea.minRightSideBearing = self.scale(hhea.minRightSideBearing)
        hhea.xMaxExtent = self.scale(hhea.xMaxExtent)

    def update_hmtx(self):
        hmtx = self.font["hmtx"]
        for gname in hmtx.metrics.keys():
            adw, lsb = hmtx.metrics[gname]
            hmtx.metrics[gname] = (self.scale(adw), self.scale(lsb))

    def update_post(self):
        post = self.font["post"]
        post.underlinePosition = self.scale(post.underlinePosition)
        post.underlineThickness = self.scale(post.underlineThickness)

    def update_vhea(self):
        if "vhea" not in self.font:
            return

        vhea = self.font["vhea"]
        vhea.ascent = self.scale(vhea.ascent)
        vhea.descent = self.scale(vhea.descent)
        vhea.lineGap = self.scale(vhea.lineGap)
        vhea.advanceHeightMax = self.scale(vhea.advanceHeightMax)
        vhea.minTopSideBearing = self.scale(vhea.minTopSideBearing)
        vhea.minBottomSideBearing = self.scale(vhea.minBottomSideBearing)
        vhea.yMaxExtent = self.scale(vhea.yMaxExtent)

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
    parser.add_argument("-u", "--upm", dest="upm", default=None,
                        help="units per EM")

    args = parser.parse_args()

    if args.out_font is None:
        args.out_font = args.in_font

    return args

def main():
    args = get_args()

    upm = 2048
    if args.upm:
        upm = float(args.upm)

    scaler = GlyphsScaler(args.in_font, args.out_font, upm)
    scaler.run()

if __name__ == "__main__":
    main()
