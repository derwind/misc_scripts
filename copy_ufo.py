#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
copy ufo via defcon
'''

import os, sys, re
import argparse
from defcon import Font, Glyph
from defcon.pens.glyphObjectPointPen import GlyphObjectPointPen

def copy_ufo(in_ufo, out_ufo, formatVersion):
    font = Font(in_ufo)

    out_font = Font()
    for attr in font.info._properties.keys():
        setattr(out_font.info, attr, getattr(font.info, attr))

    new_pgo = []

    for gname in font.lib['public.glyphOrder']:
        g = font[gname]
        g_copied = Glyph()
        for attr in ['width', 'height', 'unicodes', 'note', 'lib']:
            if hasattr(g, attr):
                setattr(g_copied, attr, getattr(g, attr))
        g_copied.width = g.width
        pen = GlyphObjectPointPen(g_copied)
        g.drawPoints(pen)
        out_font.insertGlyph(g_copied, gname)

    out_font.lib['public.glyphOrder'] = font.lib['public.glyphOrder']

    out_font.save(out_ufo, formatVersion=formatVersion)

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', dest='out_ufo', type=str, default=None, help='output ufo')
    parser.add_argument('-v', '--version', dest='version', type=int, default=2, help='formatVersion of ufo')
    parser.add_argument('in_ufo', metavar='IN_UFO', type=str, help='UFO')

    args = parser.parse_args()

    if args.out_ufo is None:
        dirname = os.path.dirname(args.in_ufo)
        basename, ext = os.path.splitext(os.path.basename(args.in_ufo))
        out_path = os.path.join(dirname, '{}.copied{}'.format(basename, ext))
        args.out_ufo = out_path

    return args

def main():
    args = get_args()
    copy_ufo(args.in_ufo, args.out_ufo, args.version)

if __name__ == '__main__':
    main()
