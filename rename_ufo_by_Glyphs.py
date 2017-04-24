#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from robofab.world import OpenFont

font = OpenFont(sys.argv[1])
pgo = font.lib["public.glyphOrder"]
new_pgo = []
for name in pgo:
    g = font[name]
    if g.note:
        g.name = g.note
    new_pgo.append(g.name)
if ".notdef" in new_pgo:
    new_pgo.remove(".notdef")
    li = [".notdef"]
    li.extend(new_pgo)
    new_pgo = li
font.lib["public.glyphOrder"] = new_pgo
font.save()
