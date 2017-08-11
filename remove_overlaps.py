#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
remove overlaps of glyphs.
"""

import sys, os, re
import argparse
from defcon import Font
from fontmake.font_project import FontProject

def mk_glyph_filter(glyphs, font):
    pgo = font.lib["public.glyphOrder"]
    gid2name = {}
    for gid, name in enumerate(pgo):
        gid2name[gid] = name

    survivors = set()

    for ranges in glyphs.split(","):
        parts = ranges.split("-")
        if len(parts) == 1:
            try:
                gid = int(parts[0])
                survivors.add(gid2name[gid])
            except:
                survivors.add(parts[0])
        else:
            start_gid = int(parts[0])
            end_gid = int(parts[1])
            for gid in range(start_gid, end_gid+1):
                survivors.add(gid2name[gid])
    return lambda g: g.name in survivors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ufos", metavar="UFO", type=str, nargs="+",
                        help="UFOs")
    parser.add_argument("-g", "--glyphs", dest="glyph_list", default=None,
                        help="target glyphs")

    args = parser.parse_args()

    paths = [re.sub(r"{}+$".format(os.sep), "", ufo) for ufo in args.ufos]
    fonts = [Font(path) for path in paths]

    glyph_filter = lambda g: True
    if args.glyph_list is not None:
        glyph_filter = mk_glyph_filter(args.glyph_list, fonts[0])

    proj = FontProject()
    proj.remove_overlaps(fonts, glyph_filter)

    for path, font in zip(paths, fonts):
        basename, _ = os.path.splitext(os.path.basename(path))
        dirname = os.path.dirname(path)
        output = os.path.join(dirname, "{}.removeOverlapped.ufo".format(basename))
        font.save(output)

if __name__ == "__main__":
    main()
