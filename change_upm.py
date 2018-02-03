#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
change units per EM
"""

import os, sys, re
import argparse
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

# https://www.microsoft.com/typography/otspec/gpos.htm
# LookupType Enumeration table for glyph positioning
class GposLookupType(object):
    SINGLE = 1
    PAIR = 2
    CURSIVE_ATT = 3
    MARK2BASE_ATT = 4
    MARK2LIGA_ATT = 5
    MARK2MARK_ATT = 6
    CONTEXT_POSITIONING = 7
    CHAINED_CONTEXT_POSITIONING = 8
    EXTENSION_POSITIONING = 9

class GlyphsScaler(object):
    def __init__(self, in_font, out_font, upm=2048, dry_run=False):
        self.in_font = in_font
        self.out_font = out_font
        self.font = TTFont(self.in_font)
        self.unitsPerEm = upm
        self._scale = round(1. * upm / self.font["head"].unitsPerEm, 3)
        self.isCID = True
        self.dry_run = dry_run
        self.updated_record_values = set()

    def run(self):
        self.update_BASE()
        if not self.dry_run:
            self.update_CFF()
        self.update_GPOS()
        self.update_OS_2()
        self.update_VORG()
        self.update_head()
        self.update_hhea()
        self.update_hmtx()
        self.update_post()
        self.update_vhea()
        self.update_vmtx()
        if not self.dry_run:
            self.font.save(self.out_font)

    def update_BASE(self):
        if "BASE" not in self.font:
            return

        base = self.font["BASE"]
        if hasattr(base.table.HorizAxis, "BaseScriptList"):
            for record in base.table.HorizAxis.BaseScriptList.BaseScriptRecord:
                for coord in record.BaseScript.BaseValues.BaseCoord:
                    coord.Coordinate = self.scale(coord.Coordinate)
        if hasattr(base.table.VertAxis, "BaseScriptList"):
            for record in base.table.VertAxis.BaseScriptList.BaseScriptRecord:
                for coord in record.BaseScript.BaseValues.BaseCoord:
                    coord.Coordinate = self.scale(coord.Coordinate)

    def update_CFF(self):
        cff = self.font["CFF "].cff
        topDict = cff.topDictIndex[0]
        self.isCID = hasattr(topDict, "FDArray")

        attrs = ["UnderlinePosition", "UnderlineThickness", "StrokeWidth"]
        self.scale_object(topDict, attrs)
        topDict.FontBBox = map(lambda v: self._scale_value(v), topDict.FontBBox)
        if self.unitsPerEm != 1000:
            topDict.rawDict["FontMatrix"] = [1./self.unitsPerEm, 0, 0, 1./self.unitsPerEm, 0, 0]

        gs = self.font.getGlyphSet()
        order = self.font.getGlyphOrder()

        self.update_glyps_widths(gs, topDict)
        self.update_default_and_nominal_width(topDict)

    # https://github.com/fonttools/fonttools/blob/master/Lib/fontTools/subset/__init__.py
    def update_glyps_widths(self, gs, topDict):
        globalSubrs = topDict.GlobalSubrs
        charStrings = topDict.CharStrings

        for name in gs.keys():
            g = gs[name]
            if self.isCID:
                c, fdSelectIndex = topDict.CharStrings.getItemAndSelector(name)
                private = topDict.FDArray[fdSelectIndex].Private
            else:
                private = topDict.Private

            dfltWdX = private.defaultWidthX
            nmnlWdX = private.nominalWidthX

            width = g.width - nmnlWdX

            transformation = (self._scale, 0, 0, self._scale, 0, 0)
            t2Pen = T2CharStringPen(width, gs)
            transPen = TransformPen(t2Pen, transformation)
            g.draw(transPen)
            charString = t2Pen.getCharString(private, globalSubrs)
            glyphID = charStrings.charStrings[name]

            self.update_glyph_width(charString, nmnlWdX)
            charStrings.charStringsIndex.items[glyphID] = charString

    def update_glyph_width(self, charString, nmnlWdX):
        int_args = []
        for b in charString.program:
            if isinstance(b, int):
                int_args.append(b)
            elif isinstance(b, str):
                if b == "rmoveto":
                    if len(int_args) != 2:
                        break
                elif b == "hmoveto" or b == "vmoveto":
                    if len(int_args) != 1:
                        break
                elif b == "endchar":
                    if len(int_args) != 0:
                        break
                else:
                    return
        charString.program[0] = self._scale_value(charString.program[0])

    def update_default_and_nominal_width(self, topDict):
        def update_private(private):
            attrs = ["defaultWidthX", "nominalWidthX"]
            self.scale_object(private, attrs)

        if self.isCID:
            for fd in topDict.FDArray:
                update_private(fd.Private)
        else:
            update_private(topDict.Private)

    def update_GPOS(self):
        if "GPOS" not in self.font:
            return

        gpos = self.font["GPOS"]
        for lookup in gpos.table.LookupList.Lookup:
            self.update_lookup(lookup)

    def update_lookup(self, lookup):
        for subtable in lookup.SubTable:
            if subtable.LookupType == GposLookupType.SINGLE:
                self.update_lookup_single(subtable)
            elif subtable.LookupType == GposLookupType.PAIR:
                self.update_lookup_pair(subtable)
            elif subtable.LookupType == GposLookupType.EXTENSION_POSITIONING:
                extSubTable = subtable.ExtSubTable
                if extSubTable.LookupType == GposLookupType.SINGLE:
                    self.update_lookup_single(extSubTable)
                elif extSubTable.LookupType == GposLookupType.PAIR:
                    self.update_lookup_pair(extSubTable)
                else:
                    pass

    def update_lookup_single(self, subtable):
        coverage = subtable.Coverage
        # SinglePosFormat1 subtable: Single positioning value
        if subtable.Format == 1:
            for gname in coverage.glyphs:
                # some fonts have odd data
                if subtable.Value is None:
                    if 0:
                        print("[WARN] {} has an invalid metrics".format(gname))
                self.update_record_value(subtable.Value)
        # SinglePosFormat2 subtable: Array of positioning values
        elif subtable.Format == 2:
            for gname, val in zip(coverage.glyphs, subtable.Value):
                self.update_record_value(val)
        else:
            raise NotImplementedError()

    def update_lookup_pair(self, subtable):
        coverage = subtable.Coverage
        # PairPosFormat1 subtable: Adjustments for glyph pairs
        if subtable.Format == 1:
            for FirstGlyph, pair in zip(coverage.glyphs, subtable.PairSet):
                for record in pair.PairValueRecord:
                    SecondGlyph = record.SecondGlyph
                    Value1 = record.Value1
                    Value2 = record.Value2
                    self.update_record_value(Value1)
        # PairPosFormat2 subtable: Class pair adjustment
        elif subtable.Format == 2:
            ordered_classes1 = self._order_classes(subtable.ClassDef1.classDefs, coverage)
            ordered_classes2 = self._order_classes(subtable.ClassDef2.classDefs)

            for classValue1, gnames1 in ordered_classes1:
                class1Record = subtable.Class1Record[classValue1]
                class2Record = class1Record.Class2Record
                for classValue2, gnames2 in ordered_classes2:
                    record = class2Record[classValue2]
                    self.update_record_value(record.Value1)
        else:
            raise NotImplementedError()

    def update_record_value(self, record):
        # If same record is referred from several lookups, then updating must be done once.
        if record in self.updated_record_values:
            return

        attrs = ["XPlacement", "YPlacement", "XAdvance", "YAdvance"]
        self.scale_object(record, attrs)

        self.updated_record_values.add(record)

    def _order_classes(self, classDefs, coverage=None):
        d = {}
        for gname, classValue in classDefs.items():
            if not classValue in d:
                d[classValue] = []
            d[classValue].append(gname)
        for classValue, gnames in d.items():
            d[classValue] = sorted(gnames)
        # XXX: precise definition of Class 0?
        # gnames = coverage - all glyphs belonging to any other classes?
        if coverage is not None and 0 not in d:
            glyphs = sorted(coverage.glyphs)
            for classValue, gnames in d.items():
                for gname in gnames:
                    if gname in glyphs:
                        glyphs.remove(gname)
            d[0] = glyphs
        # for python 2, 'lambda (classValue,gnames): gnames[0]' is also valid
        return sorted(d.items(), key=lambda classValue_gnames: classValue_gnames[1][0])

    def update_OS_2(self):
        attrs = ["xAvgCharWidth", "ySubscriptXSize", "ySubscriptYSize", "ySubscriptXOffset", "ySubscriptYOffset", "ySuperscriptXSize", "ySuperscriptYSize", "ySuperscriptXOffset", "ySuperscriptYOffset", "yStrikeoutSize", "yStrikeoutPosition", "sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent", "sxHeight", "sCapHeight"]
        self.scale_table("OS/2", attrs)

    def update_VORG(self):
        if "VORG" not in self.font:
            return

        vorg = self.font["VORG"]
        for name in vorg.VOriginRecords.keys():
            vorg.VOriginRecords[name] = self._scale_value(vorg.VOriginRecords[name])
        vorg.defaultVertOriginY = self._scale_value(vorg.defaultVertOriginY)

    def update_head(self):
        attrs = ["unitsPerEm", "xMin", "yMin", "xMax", "yMax"]
        self.scale_table("head", attrs)

    def update_hhea(self):
        attrs = ["ascent", "descent", "lineGap", "advanceWidthMax", "minLeftSideBearing", "minRightSideBearing", "xMaxExtent"]
        self.scale_table("hhea", attrs)

    def update_hmtx(self):
        hmtx = self.font["hmtx"]
        for gname in hmtx.metrics.keys():
            adw, lsb = hmtx.metrics[gname]
            hmtx.metrics[gname] = (self._scale_value(adw), self._scale_value(lsb))

    def update_post(self):
        attrs = ["underlinePosition", "underlineThickness"]
        self.scale_table("post", attrs)

    def update_vhea(self):
        if "vhea" not in self.font:
            return

        attrs = ["ascent", "descent", "lineGap", "advanceHeightMax", "minTopSideBearing", "minBottomSideBearing", "yMaxExtent"]
        self.scale_table("vhea", attrs)

    def update_vmtx(self):
        if "vmtx" not in self.font:
            return

        vmtx = self.font["vmtx"]
        for gname in vmtx.metrics.keys():
            adh, tsb = vmtx.metrics[gname]
            vmtx.metrics[gname] = (self._scale_value(adh), self._scale_value(tsb))

    def scale_table(self, table_tag, attrs):
        table = self.font[table_tag]
        self.scale_object(table, attrs)

    def scale_object(self, obj, attrs):
        for attr in attrs:
            if hasattr(obj, attr):
                setattr(obj, attr, self._scale_value(getattr(obj, attr)))

    def _scale_value(self, value):
        return int(value * self._scale)

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_font", metavar="FONT", type=str,
                        help="FONT")
    parser.add_argument("-o", "--output", dest="out_font", default=None,
                        help="output font")
    parser.add_argument("-u", "--upm", dest="upm", default=None,
                        help="units per EM")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true",
                        help="dry run?")

    args = parser.parse_args()

    if args.out_font is None:
        args.out_font = args.in_font

    return args

def main():
    args = get_args()

    upm = 2048
    if args.upm:
        upm = float(args.upm)

    scaler = GlyphsScaler(args.in_font, args.out_font, upm, args.dry_run)
    scaler.run()

if __name__ == "__main__":
    main()
