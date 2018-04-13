#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries
# date: 2017-2018
# licence: GPLv3

from doctest import run_docstring_examples
from datetime import datetime
from test_drop_alternatives import test_drop_alternatives

"""
CPU: Intel(R) Xeon(R) CPU           L5420  @ 2.50GHz
OS : Debian Jessie 8.9

2017-10-03 : 11 tests ; 3.34s ; 3.03ms/t
2017-10-03 : 11 tests ; 2.24s ; 2.06ms/t (regex del spaces ; compares 200c)
2017-10-03 : 13 tests ; 2.75s ; 2.11ms/t (deps on lxml, compares 100c)
2017-10-04 : 16 tests ; 3.56s ; 2.22ms/t (no deps, no decode, 3 junk-regex, compares 45c)
2017-10-04 : 17 tests ; 3.74s ; 2.2 ms/t (separating links regexp from junk_txt and _html)
2017-10-05 : 18 tests ; 4.11s ; 2.28ms/t (back to decode, because base64 encoding…)
2017-10-08 : 20 tests ; 4.66s ; 2.33ms/t (html.unescape, one strip regexp, compares 128c)
2017-10-13 : 21 tests ; 6.14s ; 2.92ms/t (compares 90c, from the begining, strip style & title)
2017-10-13 : 21 tests ; 5.44s ; 2.59ms/t (simplify regexp)
2017-10-18 : 22 tests ; 6,80s ; 3.09ms/t (compares 256c, use best ratio function)
2017-10-20 : 22 tests ; 6,70s ; 3.04ms/t (no more .*? nor re.DOTALL in regex)
2017-10-21 : 24 tests ; 6.64s ; 2,76ms/t (strip scripts, no more decode / bytes only)
2017-10-21 : 24 tests ; 5.43s ; 2,26ms/t (run via python2)
2017-10-21 : 25 tests ; 5.72s ; 2,28ms/t (deal with <style><!-- without .*? and re.DOTALL)
2017-10-23 : 26 tests ; 7.53s ; 2,89ms/t (deal with display:none without .*?, compares 199c)
2017-10-25 : 28 tests ; 8.22s ; 2,93ms/t (CSS /* */ proof, compares 256c backward, quick_ratio)
2017-10-26 : 28 tests ; 8.10s ; 2.89ms/t (simplify regexp, .+ -> .*, compares min(len()))
2017-11-10 : 29 tests ; 10.7s ; 3.68ms/t (keep joint files, quick_ratio() on [:256] & [-256:])
2017-11-22 : 30 tests ; 11.9s ; 3.96ms/t (read 40kc of HTML, remove all <*:…></…> which is slow)
2017-12-20 : 30 tests ; 11.2s ; 3.74ms/t (full bytes, display int ratio)

Linux 4.9.0-5-amd64 #1 SMP Debian 4.9.65-3+deb9u2 (2018-01-04) x86_64 GNU/Linux
Debian Stretch 9.3
Python 2.7.13

2018-01-11 : 30 tests ; 11.7s ; 3.91ms/t (major system update, lost perf…)
2018-03-14 : 32 tests ; 13.1s ; 4.09ms/t (remove HTML comments ; LEN=280 ; LIM=.82 ; BON=.91)
2018-03-15 : 32 tests ; 1.42s ; 4.43ms/t ( / 10 instead of / 100 in measurements)
2018-03-19 : 33 tests ; 1.50s ; 4.54ms/t (clean more ASCII art, 'cause EFF… ; slower real tests)
2018-03-20 : 34 tests ; 1.55s ; 4.55ms/t (non-breakable space is chunk delimiter, \v\f=bad c.)
2018-03-24 : 34 tests ; 1.53s ; 4.50ms/t (re-order HTML tag name of leaf to strip and bad chars)

Python 3.5.3

2018-04-11 : 34 tests ; 1.65s ; 4.85ms/t (Python 3.5.3 : +8%)
2018-04-12 : 31 tests ; 0.93s ; 3.00ms/t (major rewrite, act on message/alternative, -3fake tst)

"""

DEBUG = 0
startTime = datetime.now()

for i in range(0, 10):
	run_docstring_examples(test_drop_alternatives, globals())

print(datetime.now() - startTime)
