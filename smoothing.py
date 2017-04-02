#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re
from collections import namedtuple
from robofab.world import OpenFont
from fontTools.agl import AGL2UV

SMOOTH_THRESHOLD = 0.95

MySegment = namedtuple('MySegment', ('type', 'points', 'segment'))

if __name__ == "__main__":
    path = sys.argv[1]
    path = re.sub("{}+$".format(os.sep), "", path)
    basename, _ = os.path.splitext(os.path.basename(path))
    dirname = os.path.dirname(path)
    output_ufo = os.path.join(dirname, "{}_smoothed.ufo".format(basename))

    font = OpenFont(path)
    for g in font:
        #print "----- {} -----".format(g.name)
        for con in g:
            segments = []
            first_seg = None
            prev_seg = None
            for seg in con:
                if prev_seg is None:
                    first_seg = seg
                else:
                    if prev_seg is not None:
                        points = [prev_seg.points[-1]]
                        points.extend(seg.points)
                        myseg = MySegment(type=seg.type, points=points, segment=seg)
                        segments.append(myseg)
                prev_seg = seg
            # treat first segment
            if segments[-1].points[-1].x != first_seg.points[0].x or segments[-1].points[-1].y != first_seg.points[0].y:
                points = [segments[-1].points[-1]]
                points.extend(first_seg.points)
                myseg = MySegment(type=seg.type, points=points, segment=first_seg)
                segments.append(myseg)

            segments_len = len(segments)
            for i in range(segments_len):
                seg = segments[i]
                #print [(pt.x, pt.y) for pt in seg.points]
                next_seg = segments[(i+1)%segments_len]
                v1 = complex(seg.points[-1].x - seg.points[-2].x, seg.points[-1].y - seg.points[-2].y)
                v2 = complex(next_seg.points[1].x - next_seg.points[0].x, next_seg.points[1].y - next_seg.points[0].y)
                # When v1 and v2 have almost same direction, they are `smooth'.
                # i.e. the inner product of v1 and v2 are almost |v1|*|v2|.
                if v1.real*v2.real + v1.imag*v2.imag > abs(v1) * abs(v2) * SMOOTH_THRESHOLD:
                    seg.segment.smooth = True
    font.save(output_ufo)
