#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
all CIDs are replaced to corresponding CIDs
"""

import sys, re

TEST_STR = r"sub \913 \915 by \30000;"

# original CID: corresponding CID
CID_MAP = {
    913: 12532,
    915: 12534,
    30000: 35000
}

def conv(m):
    u"""
    :param MatchObject m: match object
    :return: converted CID representation
    :rtype: string
    """

    orig_cid = int(m.group(1))
    return r"\{}".format(CID_MAP[orig_cid])

if __name__ == "__main__":
    input_str = TEST_STR
    if len(sys.argv) > 1:
        input_str = sys.argv[1]

    #output_str = re.sub(r"\\(\d+)", lambda m: r"\{}".format(CID_MAP[int(m.group(1))]), input_str)
    output_str = re.sub(r"\\(\d+)", conv, input_str)
    print "`{}' -> `{}'".format(input_str, output_str)
