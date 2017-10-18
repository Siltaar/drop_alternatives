import doctest
from drop_alternatives import test_drop_alternatives

"""
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
"""

from datetime import datetime
startTime = datetime.now()

for i in range(0,100):
	doctest.run_docstring_examples(test_drop_alternatives, globals())

print(datetime.now() - startTime)
