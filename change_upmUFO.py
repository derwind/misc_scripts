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
                    pt.x = self._scale_value(pt.x)
                    pt.y = self._scale_value(pt.y)
            g.width = self._scale_value(g.width)

    def update_GPOS(self):
        pass

    def update_generic_dimension(self):
        attrs = ["unitsPerEm", "descender", "xHeight", "capHeight", "ascender"]
        self.scale_object(self.font.info, attrs)

    def update_hhea(self):
        attrs = ["openTypeHheaAscender", "openTypeHheaDescender", "openTypeHheaLineGap"]
        self.scale_object(self.font.info, attrs)

    def update_OS_2(self):
        attrs = ["openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap", "openTypeOS2WinAscent", "openTypeOS2WinDescent", "openTypeOS2SubscriptXSize", "openTypeOS2SubscriptYSize", "openTypeOS2SubscriptXOffset", "openTypeOS2SubscriptYOffset", "openTypeOS2SuperscriptXSize", "openTypeOS2SuperscriptYSize", "openTypeOS2SuperscriptXOffset", "openTypeOS2SuperscriptYOffset", "openTypeOS2StrikeoutSize", "openTypeOS2StrikeoutPosition"]
        self.scale_object(self.font.info, attrs)

    def update_vhea(self):
        attrs = ["openTypeVheaVertTypoAscender", "openTypeVheaVertTypoDescender", "openTypeVheaVertTypoLineGap"]
        self.scale_object(self.font.info, attrs)

    def update_postscript_specific(self):
        scale_list = lambda val: self._scale_value(val)

        attrs = ["postscriptUnderlineThickness", "postscriptUnderlinePosition", "openTypeVheaVertTypoLineGap", "postscriptDefaultWidthX", "postscriptNominalWidthX"]
        self.scale_object(self.font.info, attrs)

        attrs = ["postscriptBlueValues", "postscriptOtherBlues", "postscriptFamilyBlues", "postscriptFamilyOtherBlues", "postscriptStemSnapH", "postscriptStemSnapV"]
        self.scale_list_object(self.font.info, attrs)

    def update_vmtx(self):
        pass

    def scale_object(self, obj, attrs):
        for attr in attrs:
            if hasnoneattr(obj, attr):
                setattr(obj, attr, self._scale_value(getattr(obj, attr)))

    def scale_list_object(self, obj, attrs):
        scale_list = lambda val: self._scale_value(val)

        for attr in attrs:
            if hasnoneattr(obj, attr):
                setattr(obj, attr, map(scale_list, getattr(obj, attr)))

    def _scale_value(self, value):
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
