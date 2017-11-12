#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
change units per EM
"""

import os, sys, re
import argparse
#from robofab.world import OpenFont
from fontParts.world import OpenFont

def hasnoneattr(obj, attr):
    return hasattr(obj, attr) and getattr(obj, attr) is not None

class GlyphsScaler(object):
    def __init__(self, in_font, out_font, upm=2048, dry_run=False):
        self.in_font = in_font
        self.out_font = out_font
        self.font = OpenFont(self.in_font)
        self._scale = round(1. * upm / self.font.info.unitsPerEm, 3)
        self.dry_run = dry_run

    def run(self):
        self.update_BASE()
        if not self.dry_run:
            self.update_glif()
        self.update_GPOS()
        self.update_generic_dimension()
        self.update_hhea()
        self.update_OS_2()
        self.update_vhea()
        self.update_postscript_specific()
        self.update_vmtx()
        if not self.dry_run:
            self.font.save(self.out_font)

    def update_BASE(self):
        pass

    def update_glif(self):
        for g in self.font:
            for con in g.contours:
                for pt in con.points:
                    pt.x = self.scale(pt.x)
                    pt.y = self.scale(pt.y)
            g.width = self.scale(g.width)

    def update_GPOS(self):
        pass

    def update_generic_dimension(self):
        info = self.font.info
        info.unitsPerEm = self.scale(info.unitsPerEm)
        info.descender = self.scale(info.descender)
        info.xHeight = self.scale(info.xHeight)
        info.capHeight = self.scale(info.capHeight)
        info.ascender = self.scale(info.ascender)

    def update_hhea(self):
        info = self.font.info
        if hasnoneattr(info, "openTypeHheaAscender"):
            info.openTypeHheaAscender = self.scale(info.openTypeHheaAscender)
        if hasnoneattr(info, "openTypeHheaDescender"):
            info.openTypeHheaDescender = self.scale(info.openTypeHheaDescender)
        if hasnoneattr(info, "openTypeHheaLineGap"):
            info.openTypeHheaLineGap = self.scale(info.openTypeHheaLineGap)

    def update_OS_2(self):
        info = self.font.info
        if hasnoneattr(info, "openTypeOS2TypoAscender"):
            info.openTypeOS2TypoAscender = self.scale(info.openTypeOS2TypoAscender)
        if hasnoneattr(info, "openTypeOS2TypoDescender"):
            info.openTypeOS2TypoDescender = self.scale(info.openTypeOS2TypoDescender)
        if hasnoneattr(info, "openTypeOS2TypoLineGap"):
            info.openTypeOS2TypoLineGap = self.scale(info.openTypeOS2TypoLineGap)
        if hasnoneattr(info, "openTypeOS2WinAscent"):
            info.openTypeOS2WinAscent = self.scale(info.openTypeOS2WinAscent)
        if hasnoneattr(info, "openTypeOS2WinDescent"):
            info.openTypeOS2WinDescent = self.scale(info.openTypeOS2WinDescent)
        if hasnoneattr(info, "openTypeOS2SubscriptXSize"):
            info.openTypeOS2SubscriptXSize = self.scale(info.openTypeOS2SubscriptXSize)
        if hasnoneattr(info, "openTypeOS2SubscriptYSize"):
            info.openTypeOS2SubscriptYSize = self.scale(info.openTypeOS2SubscriptYSize)
        if hasnoneattr(info, "openTypeOS2SubscriptXOffset"):
            info.openTypeOS2SubscriptXOffset = self.scale(info.openTypeOS2SubscriptXOffset)
        if hasnoneattr(info, "openTypeOS2SubscriptYOffset"):
            info.openTypeOS2SubscriptYOffset = self.scale(info.openTypeOS2SubscriptYOffset)
        if hasnoneattr(info, "openTypeOS2SuperscriptXSize"):
            info.openTypeOS2SuperscriptXSize = self.scale(info.openTypeOS2SuperscriptXSize)
        if hasnoneattr(info, "openTypeOS2SuperscriptYSize"):
            info.openTypeOS2SuperscriptYSize = self.scale(info.openTypeOS2SuperscriptYSize)
        if hasnoneattr(info, "openTypeOS2SuperscriptXOffset"):
            info.openTypeOS2SuperscriptXOffset = self.scale(info.openTypeOS2SuperscriptXOffset)
        if hasnoneattr(info, "openTypeOS2SuperscriptYOffset"):
            info.openTypeOS2SuperscriptYOffset = self.scale(info.openTypeOS2SuperscriptYOffset)
        if hasnoneattr(info, "openTypeOS2StrikeoutSize"):
            info.openTypeOS2StrikeoutSize = self.scale(info.openTypeOS2StrikeoutSize)
        if hasnoneattr(info, "openTypeOS2StrikeoutPosition"):
            info.openTypeOS2StrikeoutPosition = self.scale(info.openTypeOS2StrikeoutPosition)

    def update_vhea(self):
        info = self.font.info
        if hasnoneattr(info, "openTypeVheaVertTypoAscender"):
            info.openTypeVheaVertTypoAscender = self.scale(info.openTypeVheaVertTypoAscender)
        if hasnoneattr(info, "openTypeVheaVertTypoDescender"):
            info.openTypeVheaVertTypoDescender = self.scale(info.openTypeVheaVertTypoDescender)
        if hasnoneattr(info, "openTypeVheaVertTypoLineGap"):
            info.openTypeVheaVertTypoLineGap = self.scale(info.openTypeVheaVertTypoLineGap)

    def update_postscript_specific(self):
        scale_list = lambda val: self.scale(val)

        info = self.font.info
        if hasnoneattr(info, "postscriptUnderlineThickness"):
            info.postscriptUnderlineThickness = self.scale(info.postscriptUnderlineThickness)
        if hasnoneattr(info, "postscriptUnderlinePosition"):
            info.postscriptUnderlinePosition = self.scale(info.postscriptUnderlinePosition)
        if hasnoneattr(info, "postscriptBlueValues"):
            info.postscriptBlueValues = map(scale_list, info.postscriptBlueValues)
        if hasnoneattr(info, "postscriptOtherBlues"):
            info.postscriptOtherBlues = map(scale_list, info.postscriptOtherBlues)
        if hasnoneattr(info, "postscriptFamilyBlues"):
            info.postscriptFamilyBlues = map(scale_list, info.postscriptFamilyBlues)
        if hasnoneattr(info, "postscriptFamilyOtherBlues"):
            info.postscriptFamilyOtherBlues = map(scale_list, info.postscriptFamilyOtherBlues)
        if hasnoneattr(info, "postscriptStemSnapH"):
            info.postscriptStemSnapH = map(scale_list, info.postscriptStemSnapH)
        if hasnoneattr(info, "postscriptStemSnapV"):
            info.postscriptStemSnapV = map(scale_list, info.postscriptStemSnapV)
        if hasnoneattr(info, "postscriptDefaultWidthX"):
            info.postscriptDefaultWidthX = self.scale(info.postscriptDefaultWidthX)
        if hasnoneattr(info, "postscriptNominalWidthX"):
            info.postscriptNominalWidthX = self.scale(info.postscriptNominalWidthX)

    def update_vmtx(self):
        pass

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
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="dry run?")

    args = parser.parse_args()

    if args.out_font is None:
        args.out_font = args.in_font

    return args

def main():
    args = get_args()

    upm = 2048
    if args.upm:
        upm = float(args.upm)

    scaler = GlyphsScaler(args.in_font, args.out_font, upm, args.dry_run)
    scaler.run()

if __name__ == "__main__":
    main()
