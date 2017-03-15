#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
find all classes/CIDs and enumerate them
"""

import sys, re

# According to https://docs.python.org/2/reference/lexical_analysis.html#indentation
#   First, tabs are replaced (from left to right) by one to eight spaces
#   such that the total number of characters up to and including the replacement
#   is a multiple of eight (this is intended to be the same rule as used by Unix).
# so tabs written below may be wide ...
TEST_STR = """
	@all_small_hira = [\842 \844 \846 \848 \850];
	@all_capital_hira = [\843 \845 \847 \849 \851];
"""[1:-1]

if __name__ == "__main__":
    input_str = TEST_STR
    if len(sys.argv) > 1:
        input_str = sys.argv[1]

    for line in re.split(r"\n", input_str):
        line = line.rstrip()
        m = re.search(r"^\s*(@\S+)\s*=\s*(.*)", line)
        if m:
            klass = m.group(1)
            latter_half_string = m.group(2)
            cids = map(lambda cid: int(cid), re.findall(r"\\(\d+)", latter_half_string))
            print "{}: {}".format(klass, cids)
