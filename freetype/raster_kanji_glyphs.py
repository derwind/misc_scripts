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

class CMapMode(object):
    NONE = 0
    CIDCHAR = 1
    CIDRANGE = 2

class CMap(object):
    def __init__(self, path):
        self.mode = CMapMode.NONE
        self.h = {}
        self.rh = {}
        self.parse(path)

    def get_cid(self, uni):
        if uni in self.h:
            return self.h[uni]
        else:
            return None

    def get_unicodes(self, cid):
        if cid in self.rh:
            return self.rh[cid]
        else:
            return None

    def parse(self, path):
        with open(path) as f:
            for line in f.readlines():
                line = line.rstrip()

                if self.mode == CMapMode.NONE:
                    if "begincidchar" in line:
                        self.mode = CMapMode.CIDCHAR
                        continue
                    elif "begincidrange" in line:
                        self.mode = CMapMode.CIDRANGE
                        continue

                elif self.mode == CMapMode.CIDCHAR:
                    if "endcidchar" in line:
                        self.mode = CMapMode.NONE
                        continue

                    m = re.search(r"<([0-9a-f]+)>\s+(\d+)", line)
                    if m:
                        uni = int(m.group(1), 16)
                        cid = int(m.group(2))
                        self.h[uni] = cid
                        if cid not in self.rh:
                            self.rh[cid] = []
                        self.rh[cid].append(uni)

                elif self.mode == CMapMode.CIDRANGE:
                    if "endcidrange" in line:
                        self.mode = CMapMode.NONE
                        continue

                    m = re.search(r"<([0-9a-f]+)>\s+<([0-9a-f]+)>\s+(\d+)", line)
                    if m:
                        uni_start = int(m.group(1), 16)
                        uni_end = int(m.group(2), 16)
                        cid = int(m.group(3))
                        for i in range(uni_end-uni_start+1):
                            self.h[uni_start+i] = cid+i
                            if cid+i not in self.rh:
                                self.rh[cid+i] = []
                            self.rh[cid+i].append(uni_start+i)

            for cid, unicodes in self.rh.items():
                self.rh[cid] = sorted(self.rh[cid])

def parse_charset(charset):
    d = {}
    with open(charset) as f:
        for line in f.readlines():
            m = re.search(r"^(\d+)\s+(\S+)\s+", line)
            if m:
                cid = int(m.group(1))
                typ = m.group(2)
                if typ not in d:
                    d[typ] = []
                d[typ].append(cid)
    for typ in d.keys():
        d[typ] = sorted(d[typ])
    return d

# https://github.com/rougier/freetype-py/blob/master/examples/agg-trick.py
def save_image(face, cid):
    gid = cid
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
    im.save("cid{0:05d}.png".format(cid), "PNG")

def main():
    font_path = sys.argv[1]
    #cmap = CMap(sys.argv[2])
    charset = parse_charset(sys.argv[2])

    face = freetype.Face(font_path)
    size = int(UPM * ratio)
    hres = 72
    face.set_char_size( size*64, 0, hres, 72 )
    for cid in charset["Kanji"]:
        if cid > 9353:
            break
        save_image(face, cid)

if __name__ == "__main__":
    main()
