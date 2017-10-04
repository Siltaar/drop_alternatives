#!/usr/bin/python3
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


from __future__ import print_function
from io import TextIOWrapper
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
import sys
import re


DEBUG = True
DEBUG = False
COMPARED_SIZE = 45
re_light_decode = re.compile('=\n')
re_strip = re.compile('https?://[^ >]+|\s+|\n+|\t+')
re_junk_txt = re.compile('\*+|-+|#+|\[.*?\]|<.*?>')
re_junk_html= re.compile('C2=A0|=09|(<|^).*?>|&nbsp;|=+')


def debug(s):
    if DEBUG:
        print(s, file=sys.stderr)


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
		debug(' ')
		kept_parts = []
		html_parts = []
		texts = []

		for part in eml.walk():
			if (part.get_content_maintype() == "multipart" or
				part.get_content_type() == "message/external-body" or
				part.get_payload() == ""):
				continue
			elif part.get_content_type() == "text/plain":
				kept_parts.append(part)
				texts.append(part.get_payload()[-20*COMPARED_SIZE:])
			elif part.get_content_type() == "text/html":
				html_parts.append(part)
			else:
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt = h.get_payload()[-76*COMPARED_SIZE:]
				h_txt = re.sub(re_light_decode, '', h_txt)
				h_txt = re.sub(re_strip, '', h_txt)
				# debug(h_txt)
				h_txt = re.sub(re_junk_html, '', h_txt)
				h_txt = h_txt[-COMPARED_SIZE:]

				save_html = True

				for i, t in enumerate(texts):
					t = re.sub(re_light_decode, '', t)
					t = re.sub(re_strip, '', t)
					t = re.sub(re_junk_txt, '', t)
					t = t[-COMPARED_SIZE:]

					diff_ratio = SequenceMatcher(None, a=h_txt, b=t).quick_ratio()
					debug(h_txt+' '+t+' '+str(round(diff_ratio, 2)))

					if diff_ratio > 0.66:
						save_html = False
						recompose_msg = True
						del texts[i]  # avoid comparing again with this text

				if save_html:
					kept_parts.append(h)

			if recompose_msg:
				return compose_message(eml, kept_parts)

	return eml


def test_drop_alternatives(msg_str):
	"""
	>>> test_drop_alternatives('Content-Type: text/plain;\\nA')
	text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<body>A</body><style><!--body{color red;}--></style>')
	multipart/mixed;text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>\\t\\t\\t\\t\\t\\t\\t<p>A</p>')
	multipart/mixed;text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html>B')
	multipart/mixed;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB')
	multipart/mixed;text/plain;text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\n<p>C</p>')
	multipart/mixed;text/plain;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nB\\n'
	... '--\\nContent-Type: text/html;\\nC')
	multipart/mixed;text/plain;text/plain;text/html;
	>>> test_drop_alternatives(open('test_email/20160916.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20170901.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20170917.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20170925.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171003.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171003-2.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171004.eml', errors='ignore').read())
	multipart/mixed;text/plain;text/plain;
	>>> test_drop_alternatives(open('test_email/20171004-2.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171004-3.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171004-4.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	"""
	for p in drop_alternatives(msg_str).walk():
		print(p.get_content_type(), end=';')
		# debug(str(p.get_payload()))
	print('')


if __name__ == "__main__":
	print(drop_alternatives(TextIOWrapper(sys.stdin.buffer, errors='ignore').read()))
