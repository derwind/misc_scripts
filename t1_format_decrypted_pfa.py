#! /usr/bin/evn python
# -*- coding: utf-8 -*-

import sys, os, re

def stack_operands_operator(line, stack):
    line = line.strip()
    operands = []
    for v in re.split(r"\s+", line):
        if re.match(r"-?\d+", v):
            #operands.append(int(v))
            operands.append(v)
        else:
            stack.append( (operands, v) )
            operands = []

def main():
    with open(sys.argv[1]) as f:
        operands_operator = []
        prefix = suffix = None
        in_outline = False
        for line in f.readlines():
            line = line.rstrip()
            if "## -| {" in line:
                former, latter = line.split("## -| {")
                prefix = former + "## -| {"
                line = latter
                in_outline = True
            if "} |" in line:
                former, latter = line.split("} |")
                line = former
                suffix = "} |" + latter

            if in_outline:
                stack_operands_operator(line, operands_operator)
                if suffix is not None:
                    print prefix
                    for operands, operator in operands_operator:
                        print " ",
                        if operands:
                            print " ".join(operands),
                        print operator
                    print suffix
                    operands_operator = []
                    prefix = suffix = None
                    in_outline = False
            else:
                print line

if __name__ == "__main__":
    main()
