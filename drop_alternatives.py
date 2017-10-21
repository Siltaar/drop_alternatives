#!/usr/bin/python3
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


from __future__ import print_function
from io import TextIOWrapper
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
from sys import stdin, stderr
import re


DEBUG = 0
re_strip = re.compile(b'<(tit|sty|scr|o:)[^>]+>[^<]+</[^>]+>|<[^>]+>|https?://[^ >]+|&[^;]+;')
bad_char = b' \n\r\t-*#:>|=.'


def compose_message(orig, parts):
	wanted = MIMEMultipart()
	unwanted_fields = ["content-length", "content-type", "lines", "status"]

	for field in unwanted_fields:
		del orig[field]

	for k, v in orig.items():  # `orig` have only headers as its items
		wanted[k] = v

	for p in parts:
		wanted.attach(p)

	return wanted


def drop_alternatives(msg_str):
	eml = Parser().parsestr(msg_str);

	if eml.is_multipart():
		kept_parts = []
		html_parts = []
		texts = []

		if DEBUG: print('', file=stderr)
		for part in eml.walk():
			# if DEBUG: print(part.get_content_type(), file=stderr)
			if ("multipart" in part.get_content_maintype() or
				"message" in part.get_content_type() or
				part.get_payload() == ""):
				continue
			elif 'html' in part.get_content_type():
				html_parts.append(part)
			elif 'plain' in part.get_content_type():
				kept_parts.append(part)
				texts.append(get_txt(part, 2560))
			else:
				# if DEBUG: print('kept '+part.get_content_type(), file=stderr)
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt = get_txt(h, 28000)
				save_html = True

				for i, t in enumerate(texts):
					idem_ratio = SequenceMatcher(None,a=h_txt, b=t).ratio()
					if DEBUG:
						print(b'h: '+h_txt, file=stderr)
						print(b't: '+t, file=stderr, end=' ')
						print(idem_ratio, file=stderr)

					if idem_ratio > 0.50:
						save_html = False
						recompose_msg = True
						del texts[i]  # avoid comparing again with this text
						break

				if save_html:
					kept_parts.append(h)

			if recompose_msg:
				return compose_message(eml, kept_parts)

	return eml


def get_txt(part, raw_len, bad_char=bad_char):
	t = part.get_payload(decode=True)[:raw_len]
	t = re_strip.sub(b'', t)
	t = t.translate(None, bad_char)
	return t[:256]


def test_drop_alternatives(msg_str):
	"""
	>>> test_drop_alternatives('Content-Type: text/plain;\\nA')
	text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<body>A</body><style><!--body{color red;}--></style>')
	multipart/mixed text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>\\t\\t\\t\\t\\t\\t\\t<p>A</p>')
	multipart/mixed text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>B')
	multipart/mixed text/plain text/html
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB')
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\n<p>C</p>')
	multipart/mixed text/plain text/plain text/html
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nC')
	multipart/mixed text/plain text/plain text/html
	>>> test_drop_alternatives(open('test_email/20160916.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170901.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170917.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170925.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171003.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171003-2.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004.eml', errors='ignore').read())
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives(open('test_email/20171004-2.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-3.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-4.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-5.eml', errors='ignore').read())
	multipart/mixed text/plain text/plain text/plain
	>>> test_drop_alternatives(open('test_email/20171005.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171005-3.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171011.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018-2.eml', errors='ignore').read())
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171020.eml', errors='ignore').read())
	multipart/mixed text/plain
	"""
	print(' '.join([p.get_content_type() for p in drop_alternatives(msg_str).walk()]))


if __name__ == "__main__":
	print(drop_alternatives(TextIOWrapper(stdin.buffer, errors='ignore').read()))
