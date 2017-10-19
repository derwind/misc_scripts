#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
import struct
import freetype
import numpy as np
from PIL import Image

UPM = 1000
DESCENDER = 120

ratio = .5

# https://github.com/rougier/freetype-py/blob/master/examples/agg-trick.py
def save_image(face, gid):
    face.load_glyph(gid)
    bitmap = face.glyph.bitmap
    width, height = bitmap.width, bitmap.rows
    left, top = face.glyph.bitmap_left, face.glyph.bitmap_top
    shift = int(DESCENDER * ratio)
    #print "{}x{}".format(width, height)
    W, H = int(UPM * ratio), int(UPM * ratio)
    Z = np.zeros( (H, W), dtype=np.ubyte )
    if True:
        buff = np.array(bitmap.buffer, dtype=np.ubyte).reshape((height, width))
        Z[H-(top+shift):H-(top+shift)+height,left:left+width].flat |= buff[:,:width].flatten()
        Z = 0xff - Z
        im = Image.fromarray(Z, mode='L')
    else:
        data = ''.join([struct.pack('B', 255-c) for c in bitmap.buffer])
        im = Image.frombuffer("L", (bitmap.width, bitmap.rows), data, "raw", "L", 0, 1)
    im.save("{}.png".format(gid), "PNG")

def main():
    font_path = sys.argv[1]
    face = freetype.Face(font_path)
    size = int(UPM * ratio)
    hres = 72
    face.set_char_size( size*64, 0, hres, 72 )
    for gid in range(1125, 1130+1):
        save_image(face, gid)

if __name__ == "__main__":
    main()
