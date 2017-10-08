import doctest
from drop_alternatives import test_drop_alternatives

"""
2017-10-03 : 11 tests ; 3.34s ; 0.303s/t
2017-10-03 : 11 tests ; 2.24s ; 0.206s/t (regex del spaces ; compares 200c)
2017-10-03 : 13 tests ; 2.75s ; 0.211s/t (deps on lxml, compares 100c)
2017-10-04 : 16 tests ; 3.56s ; 0.222s/t (no deps, no decode, 3 junk-regex, compares 45c)
2017-10-04 : 17 tests ; 3.74s ; 0.22 s/t (separating links regexp from junk_txt and _html)
2017-10-05 : 18 tests ; 4.11s ; 0.228s/t (back to decode, because base64 encoding…)
2017-10-08 : 20 tests ; 4.66s ; 0.233s/t (html.unescape, one strip regexp, compares 128c)
"""

from datetime import datetime
startTime = datetime.now()

for i in range(0,100):
	doctest.run_docstring_examples(test_drop_alternatives, globals())

print(datetime.now() - startTime)
