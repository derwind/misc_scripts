#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from distutils.spawn import find_executable

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

if __name__ == "__main__":
    def default_cmap_path():
        try:
            tx_path = os.path.dirname(find_executable("tx"))
            path = os.path.join(tx_path, "../SharedData/Adobe Cmaps/Adobe-Japan1")
            return os.path.join(path, "UniJIS2004-UTF32-H")
        except:
            return None

    cmap_path = default_cmap_path()
    if len(sys.argv) > 1:
        cmap_path = sys.argv[1]
    cmap = CMap(cmap_path)
    for uni, cid in sorted(cmap.h.items(), key=lambda (uni, cid): cid):
        print "{0:04x}: {1}".format(uni, cid)
    print "-"*50
    for cid, unicodes in sorted(cmap.rh.items(), key=lambda (cid, unicodes): cid):
        print "{}: {}".format(cid, ", ".join(map(lambda uni: "{0:04x}".format(uni), unicodes)))
