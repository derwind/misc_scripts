#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
split and join glyphs
"""

import os, sys, re
import argparse
from robofab.world import OpenFont
from robofab.objects.objectsRF import RGlyph

CONTOURS_THRESHOLD = 256
Y_THRESHOLD = 380

class UfoSplitter(object):
    def __init__(self, in_ufo, out_ufo, join=False):
        self.in_ufo = in_ufo
        self.out_ufo = out_ufo
        self.join = join

    def run(self):
        font = OpenFont(self.in_ufo)
        if self.join:
            self.join_glyphs(font)
        else:
            self.split_glyphs(font)
        font.save(self.out_ufo)

    def split_glyphs(self, font):
        new_pgo = []
        for gname in font.lib["public.glyphOrder"]:
            g = font[gname]
            if len (g.contours) > CONTOURS_THRESHOLD:
                upper = g.copy()
                upper.clear()
                upper.name = "{}.upper".format(g.name)
                lower = g.copy()
                lower.clear()
                lower.name = "{}.lower".format(g.name)
                for con in g.contours:
                    ymin = min([pt.y for pt in con.points])
                    if ymin >= Y_THRESHOLD:
                        upper.appendContour(con)
                    else:
                        lower.appendContour(con)
                font.insertGlyph(upper)
                font.insertGlyph(lower)
                new_pgo.append(upper.name)
                new_pgo.append(lower.name)
                font.removeGlyph(g.name)
            else:
                new_pgo.append(g.name)
        font.lib["public.glyphOrder"] = sorted(new_pgo)

    def join_glyphs(self, font):
        new_pgo = []
        for gname in font.lib["public.glyphOrder"]:
            g = font[gname]
            suffix = g.name.split(".")[-1]
            if suffix == "lower":
                continue
            elif suffix == "upper":
                parent_name = g.name.split(".")[0]
                g.name = parent_name
                lower_g = font["{}.lower".format(parent_name)]
                for con in lower_g:
                    g.appendContour(con)
                new_pgo.append(parent_name)
                font.removeGlyph(lower_g.name)
            else:
                new_pgo.append(g.name)
        font.lib["public.glyphOrder"] = sorted(new_pgo)

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_ufo", metavar="UFO", type=str,
                        help="input ufo")
    parser.add_argument("-o", "--output", dest="out_ufo", default=None,
                        help="output ufo")
    parser.add_argument("-j", "--join", dest="join", action="store_true",
                        help="join glyphs?")

    args = parser.parse_args()

    if args.out_ufo is None:
        args.out_ufo = args.in_ufo

    return args

def main():
    args = get_args()

    ufo_splitter = UfoSplitter(args.in_ufo, args.out_ufo, args.join)
    ufo_splitter.run()

if __name__ == "__main__":
    main()
