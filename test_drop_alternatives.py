import doctest
from drop_alternatives import test_drop_alternatives

"""
2017-10-03 : 3.34s -> 2.24s (regex to normalize spaces ; compared sizes restricted to 200)
2017-10-03 : 2.75s (new cases, compared sizes shrinked to 100)
"""

from datetime import datetime
startTime = datetime.now()

for i in range(0,100):
	doctest.run_docstring_examples(test_drop_alternatives, globals())

print(datetime.now() - startTime)
