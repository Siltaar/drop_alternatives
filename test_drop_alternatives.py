#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from doctest import run_docstring_examples
from drop_alternatives import drop_alternatives


DEBUG = 0


def test_drop_alternatives(msg_bytes, debug):
	"""
    >>> test_drop_alternatives(b'Content-Type: text/plain;\\nA', DEBUG)
    text/plain
    >>> test_drop_alternatives(b'Content-Type: multipart/mixed; boundary=""\\n'
    ... b'--\\nContent-Type: multipart/alternative;\\n'
    ... b'--\\nContent-Type: text/plain;\\nA\\n'
    ... b'--\\nContent-Type: text/html;\\n <sty> B <!-- D -->/* C */\\n</sty>A', DEBUG)
    multipart/mixed text/plain
    >>> test_drop_alternatives(b'Content-Type: multipart/mixed; boundary=""\\n'
    ... b'--\\nContent-Type: multipart/alternative;\\n'
    ... b'--\\nContent-Type: text/plain;\\nA\\n'
    ... b'--\\nContent-Type: text/html;\\n<html>\\t\\t\\t\\t\\t\\t\\t<p>A</p>', DEBUG)
    multipart/mixed text/plain
    >>> test_drop_alternatives(b'Content-Type: multipart/mixed; boundary=""\\n'
    ... b'--\\nContent-Type: multipart/alternative;\\n'
    ... b'--\\nContent-Type: text/plain;\\nA\\n'
    ... b'--\\nContent-Type: text/html;\\n<html>B', DEBUG)
    multipart/mixed text/plain text/html
    >>> test_drop_alternatives(b'Content-Type: multipart/mixed; boundary=""\\n'
    ... b'--\\nContent-Type: text/plain;\\nA\\n'
    ... b'--\\nContent-Type: multipart/alternative;\\n'
    ... b'--\\nContent-Type: text/plain;\\nB\\n'
    ... b'--\\nContent-Type: text/html;\\nB', DEBUG)
    multipart/mixed text/plain text/plain
    >>> test_drop_alternatives(b'Content-Type: multipart/mixed; boundary=""\\n'
    ... b'--\\nContent-Type: text/plain;\\nA\\n'
    ... b'--\\nContent-Type: text/plain;\\nB\\n'
    ... b'--\\nContent-Type: text/html;\\n<p>C</p>', DEBUG)
    multipart/mixed text/plain text/plain text/html
	>>> test_drop_alternatives(open('email_test/20160916.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20170901.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20170917.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20170925.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171003.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171003-2.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171004.eml', 'rb').read(), DEBUG)
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives(open('email_test/20171004-2.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171004-3.eml', 'rb').read(), DEBUG)
	multipart/mixed text/plain multipart/external-body application/octet-stream
	>>> test_drop_alternatives(open('email_test/20171004-4.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171004-5.eml', 'rb').read(), DEBUG)
	multipart/mixed text/plain multipart/rfc822 text/plain text/plain
	>>> test_drop_alternatives(open('email_test/20171005.eml', 'rb').read(), DEBUG)
	multipart/related text/plain multipart/external-body image/png
	>>> test_drop_alternatives(open('email_test/20171005-3.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171011.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171018.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171018-2.eml', 'rb').read(), DEBUG)
	multipart/mixed text/plain multipart/external-body application/pdf
	>>> test_drop_alternatives(open('email_test/20171018-3.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171020.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171022.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171023.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171025.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20171109.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain text/plain
	>>> test_drop_alternatives(open('email_test/20180312.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20180314.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20180315.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20180319.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20180320.eml', 'rb').read(), DEBUG)
	multipart/alternative text/plain
	>>> test_drop_alternatives(open('email_test/20180402.eml', 'rb').read(), DEBUG)
	text/html
	"""
	print(' '.join([p.get_content_type() for p in drop_alternatives(msg_bytes, debug).walk()]))


if __name__ == "__main__":
	run_docstring_examples(test_drop_alternatives, globals())
