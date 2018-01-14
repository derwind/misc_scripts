#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
import argparse
from robofab.world import OpenFont

class RotatedGlyphsAdjuster(object):
    def __init__(self, in_ufo, out_ufo, cid_shift=8719, features="features.fea", original_ufo=None):
        self.in_ufo = in_ufo
        self.out_ufo = out_ufo
        self.cid_shift = cid_shift
        self.features = features
        self.original_ufo = original_ufo

    def run(self):
        font = OpenFont(self.in_ufo)
        original_font = None
        if self.original_ufo is not None:
            original_font = OpenFont(self.original_ufo)

        from_to = {}
        widths = {}
        pgo = []
        for gname in font.lib["public.glyphOrder"]:
            g = font[gname]
            g.unicodes = []
            from_cid = int(gname.replace("cid", ""))
            to_cid = from_cid + self.cid_shift
            new_gname = "cid{0:05d}".format(to_cid)
            pgo.append(new_gname)
            g.name = new_gname
            from_to[from_cid] = to_cid
            if original_font is None:
                widths[to_cid] = g.width
            else:
                widths[to_cid] = original_font[gname].width

        font.lib["public.glyphOrder"] = pgo
        with open(self.features, "w") as f:
            print>>f, "feature vert {"
            for from_cid, to_cid in sorted(from_to.items()):
                print>>f, "  sub \\{} by \\{};".format(from_cid, to_cid)
            print>>f, "} vert;"
            print>>f, "feature vmtx {"
            for cid, width in sorted(widths.items()):
                print>>f, "  VertAdvanceY \\{} {};".format(cid, width)
            print>>f, "} vmtx;"

        font.info.ascender = 880
        font.info.descender = -120

        font.save(self.out_ufo)

        return 0

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_ufo", metavar="FONT", type=str,
                        help="input ufo")
    parser.add_argument("-o", "--output", dest="out_ufo", metavar="OUT_UFO", type=str, default=None,
                        help="output ufo")
    parser.add_argument("-c", "--cid-shift", dest="cid_shift", metavar="CID_SHIFT", type=int, default=8719,
                        help="CID value to be shifted")
    parser.add_argument("-f", "--features", dest="features", metavar="FEATURES", type=str, default="features.fea",
                        help="features file name")
    parser.add_argument("--original", dest="original_ufo", metavar="ORIGINAL_UFO", type=str, default=None,
                        help="not rotated ufo")

    args = parser.parse_args()

    if args.out_ufo is None:
        args.out_ufo = args.in_ufo

    return args

def main():
    args = get_args()

    tool = RotatedGlyphsAdjuster(args.in_ufo, args.out_ufo, args.cid_shift, args.features, args.original_ufo)
    sys.exit(tool.run())

if __name__ == "__main__":
    main()
