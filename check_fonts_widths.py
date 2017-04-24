#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from fontTools.ttLib import TTFont
from robofab.world import OpenFont
from distutils.spawn import find_executable

UPM = 1000

class Layout(object):
    def __init__(self, layout_path):
        self.h = {}
        self.parse(layout_path)

    def parse(self, layout_path):
        with open(layout_path) as f:
            for line in f.readlines():
                line = line.rstrip()
                cid, fd_array, row, name = re.split(r"\s+", line)
                cid = int(cid)
                self.h[cid] = (fd_array, row)

    def is_half(self, cid):
        return "Rot" not in self.h[cid][0] and (re.match(r"H[A-Z]", self.h[cid][0]) or re.match(r"H[A-Z]", self.h[cid][1]))

    def is_proportional(self, cid):
        return self.h[cid][0].startswith("Proportional") or self.h[cid][1].startswith("Proportional")

def default_layout_path():
    try:
        tx_path = os.path.dirname(find_executable("tx"))
        path = os.path.join(tx_path, "../SharedData/CID charsets")
        return os.path.join(path, "AJ16-J15")
    except:
        return None

def otf_proc(font_path, layout):
    font = TTFont(font_path)
    gs = font.getGlyphSet()
    cids = set()
    for name in gs.keys():
        if name == ".notdef":
            continue
        cids.add(int(name.replace("cid", "")))

    ng_cnt = 0
    for cid in sorted(cids):
        name = "cid{0:05d}".format(cid)
        g = gs[name]
        if layout.is_half(cid):
            if g.width != UPM/2:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1
        elif layout.is_proportional(cid):
            pass
        else:
            if g.width != UPM:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1

    print "-"*50
    print "{}% are incorrect".format(round(100.*ng_cnt/len(cids), 2))

def ufo_proc(font_path, cmap):
    font = OpenFont(font_path)
    ng_cnt = 0
    for name in font.lib["public.glyphOrder"]:
        if name == ".notdef":
            continue
        g = font[name]
        cid = int(name.replace("cid", ""))
        if cid <= 1:
            continue

        if layout.is_half(cid):
            if g.width != UPM/2:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1
        elif layout.is_proportional(cid):
            pass
        else:
            if g.width != UPM:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1

    print "-"*50
    print "{}% are incorrect".format(round(100.*ng_cnt/len(font.lib["public.glyphOrder"]), 2))

if __name__ == "__main__":
    font_path = sys.argv[1]
    font_path = re.sub(r"{}+$".format(os.sep), "", font_path)
    basename, ext = os.path.splitext(os.path.basename(font_path))

    layout_path = default_layout_path()
    if len(sys.argv) > 2:
        layout_path = sys.argv[2]

    layout = Layout(layout_path)

    if ext == ".otf" or ext == ".ttf":
        otf_proc(font_path, layout)
    elif ext == ".ufo":
        ufo_proc(font_path, layout)
