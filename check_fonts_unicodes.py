#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from fontTools.ttLib import TTFont
from robofab.world import OpenFont
from distutils.spawn import find_executable
from cmap_reader import CMap

def default_cmap_path():
    try:
        tx_path = os.path.dirname(find_executable("tx"))
        path = os.path.join(tx_path, "../SharedData/Adobe Cmaps/Adobe-Japan1")
        return os.path.join(path, "UniJIS2004-UTF32-H")
    except:
        return None

def otf_proc(font_path, cmap):
    font = TTFont(font_path)
    """
    gs = font.getGlyphSet()
    cids = set()
    for name in gs.keys():
        if name == ".notdef":
            continue
        cids.add(int(name.replace("cid", "")))
    for cid in sorted(cids):
        name = "cid{0:05d}".format(cid)
        g = gs[name]
        print g.unicodes
    """
    cmap_ = font["cmap"].getcmap(platformID=0, platEncID=3)

    # XXX: only cmap_format_4 is assumed
    ng_cnt = 0
    for uni, name in cmap_.cmap.items():
        cid = int(name.replace("cid", ""))
        if cid <= 1:
            continue
        try:
            if cmap.h[uni] != cid:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1
        except:
            print "[{}] ! {}".format(ng_cnt, name)
            ng_cnt += 1
    print "-"*50
    print "{}% are incorrect".format(round(100.*ng_cnt/len(cmap_.cmap), 2))

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
        try:
            ng = False
            for uni in g.unicodes:
                if cmap.h[uni] != cid:
                    ng = True
            if ng:
                print "[{}] + {}".format(ng_cnt, name)
                ng_cnt += 1
        except:
            print "[{}] ! {}".format(ng_cnt, name)
            ng_cnt += 1
    print "-"*50
    print "{}% are incorrect".format(round(100.*ng_cnt/len(font.lib["public.glyphOrder"]), 2))

if __name__ == "__main__":
    font_path = sys.argv[1]
    font_path = re.sub(r"{}+$".format(os.sep), "", font_path)
    basename, ext = os.path.splitext(os.path.basename(font_path))

    cmap_path = default_cmap_path()
    if len(sys.argv) > 2:
        cmap_path = sys.argv[2]

    cmap = CMap(cmap_path)

    if ext == ".otf" or ext == ".ttf":
        otf_proc(font_path, cmap)
    elif ext == ".ufo":
        ufo_proc(font_path, cmap)
