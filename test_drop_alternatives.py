#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from doctest import run_docstring_examples
from drop_alternatives import drop_alternatives


DEBUG = 1


def test_drop_alternatives(msg_str, debug):
	"""
	>>> test_drop_alternatives('Content-Type: text/plain;\\nA', DEBUG)
	text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n <sty> B <!-- D -->/* C */\\n</sty>A', DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>\\t\\t\\t\\t\\t\\t\\t<p>A</p>', DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>B', DEBUG)
	multipart/mixed text/plain text/html
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB', DEBUG)
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\n<p>C</p>', DEBUG)
	multipart/mixed text/plain text/plain text/html
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nC', DEBUG)
	multipart/mixed text/plain text/plain text/html
	>>> test_drop_alternatives(open('email_test/20160916.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20170901.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20170917.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20170925.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171003.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171003-2.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171004.eml').read(), DEBUG)
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives(open('email_test/20171004-2.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171004-3.eml').read(), DEBUG)
	multipart/mixed text/plain application/octet-stream
	>>> test_drop_alternatives(open('email_test/20171004-4.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171004-5.eml').read(), DEBUG)
	multipart/mixed text/plain text/plain text/plain
	>>> test_drop_alternatives(open('email_test/20171005.eml').read(), DEBUG)
	multipart/mixed text/plain image/png
	>>> test_drop_alternatives(open('email_test/20171005-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171011.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171018.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171018-2.eml').read(), DEBUG)
	multipart/mixed text/plain application/pdf
	>>> test_drop_alternatives(open('email_test/20171018-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171020.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171022.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171023.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171025.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20171109.eml').read(), DEBUG)
	multipart/mixed text/plain image/png
	>>> test_drop_alternatives(open('email_test/20180312.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20180314.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20180315.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20180319.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('email_test/20180320.eml').read(), DEBUG)
	multipart/mixed text/plain
	"""
	print(' '.join([p.get_content_type() for p in drop_alternatives(msg_str, debug).walk()]))


if __name__ == "__main__":
	run_docstring_examples(test_drop_alternatives, globals())
