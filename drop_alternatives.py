#!/usr/bin/python3
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


from __future__ import print_function
from io import TextIOWrapper
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
import sys, re, html


DEBUG = True
DEBUG = False
COMPARED_SIZE = 128
re_strip = re.compile('<style>.*?</style>|\[[^\]]+\]|<[^>]+>|https?://[^ \n><]+|[\s\n\-*#:>|]+', re.DOTALL)


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
		if DEBUG: print(' ', file=sys.stderr)
		kept_parts = []
		html_parts = []
		texts = []

		for part in eml.walk():
			if ("multipart" in part.get_content_maintype() or
				"message" in part.get_content_type() or
				part.get_payload() == ""):
				continue
			elif 'html' in part.get_content_type():
				html_parts.append(part)
			elif 'text' in part.get_content_type():
				kept_parts.append(part)
				t = part.get_payload(decode=True).decode(
					part.get_content_charset() or 'utf-8', 'ignore')[-10*COMPARED_SIZE:]
				t = re.sub(re_strip, '', t)
				t = t[-COMPARED_SIZE:]
				texts.append(t)
			else:
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt = h.get_payload(decode=True).decode(
					part.get_content_charset() or 'utf-8', 'ignore')[-50*COMPARED_SIZE:]
				h_txt = html.unescape(h_txt)
				h_txt = re.sub(re_strip, '', h_txt)
				h_txt = h_txt[-COMPARED_SIZE:]

				save_html = True

				for i, t in enumerate(texts):
					diff_ratio = SequenceMatcher(None, a=h_txt, b=t).quick_ratio()
					if DEBUG: print(h_txt+' '+t+' '+str(round(diff_ratio, 2)), file=sys.stderr)

					if diff_ratio > 0.75:
						save_html = False
						recompose_msg = True
						del texts[i]  # avoid comparing again with this text
						break

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
	>>> test_drop_alternatives(open('test_email/20171004-5.eml', errors='ignore').read())
	multipart/mixed;text/plain;text/plain;text/plain;
	>>> test_drop_alternatives(open('test_email/20171005.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	>>> test_drop_alternatives(open('test_email/20171005-3.eml', errors='ignore').read())
	multipart/mixed;text/plain;
	"""
	for p in drop_alternatives(msg_str).walk():
		print(p.get_content_type(), end=';')
	print('')


if __name__ == "__main__":
	print(drop_alternatives(TextIOWrapper(sys.stdin.buffer, errors='ignore').read()))
