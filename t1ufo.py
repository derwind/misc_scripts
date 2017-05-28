#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from fontTools.t1Lib import T1Font
from robofab.world import RFont, RGlyph
from robofab.pens.rfUFOPen import RFUFOPen

if __name__ == "__main__":
    path = sys.argv[1]
    t1_font = T1Font(path)

    font = RFont()
    pgo = []

    for gname, charstring in t1_font["CharStrings"].items():
        pgo.append(gname)
        glyph = RGlyph()
        pen = RFUFOPen(glyph)
        charstring.draw(pen)
        font.insertGlyph(glyph, gname)

    font.lib["public.glyphOrder"] = pgo
    font.save("test.ufo")
