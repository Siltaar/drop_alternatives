#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-10
# licence: GPLv3

from __future__ import print_function
from io import TextIOWrapper
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
from sys import stdin, stderr, version_info
from re import DOTALL, compile as compile_re


re_html = compile_re(
	# b'(<(tit|sty|scr|[^y]*y:n)|^).*?</(tit|sty|scr)[^>]*|(<|^)[^>]*>|[\d*]|&[^;]*;|[^\s\n\r<]{25,}',
	b'<(tit|sty|scr|o:P|[^y]*y:n).*?</[^>]*|<[^>]*|[\d*]|&[^;]*;|[^\s\n\r<]{25,}',
	# match and so remove :
	# - title, style, script, o:PixelsPerInch, display:none HTML tags and their text leafs
	# - all HTML tags,  # even if cut at the begining
	# - links prefix in converted texts
	# - HTML entities
	# - chunks of symbols without spaces too big to be words (such as URL)
	DOTALL)
bad_char = b' \t\n\r\xc2\xa0\'#->=:*]['  # exist: \v Vertical tab ; \f From feed
W  = b'\033[0m'  # white (normal)
G  = b'\033[1;30m' # grey
R  = b'\033[1;31m' # bold red
Y  = b'\033[1;33m' # bold yellow
B  = b'\033[1;37m' # bold white

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


def drop_alternatives(msg_str, debug=0):
	eml = Parser().parsestr(msg_str)

	if eml.is_multipart():
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
			elif 'plain' in part.get_content_type():
				kept_parts.append(part)
				texts.append(get_txt(part, 2500))
			else:
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt = get_txt(h, 15000)
				len_h_txt = len(h_txt)
				save_html = True

				for i, t in enumerate(texts):
					s = min(len_h_txt, len(t))
					idem_ratio = SequenceMatcher(None, a=h_txt[-s:], b=t[-s:]).quick_ratio()

					if debug:
						print((not i and G or B) + h_txt + W + ' H', file=stderr)
						print(t+' T', file=stderr, end=' ')
						C = idem_ratio < 0.85 and R or idem_ratio < 0.90 and Y or W
						print(C + bytes(idem_ratio)[:5] + W, file=stderr)

					if idem_ratio > 0.85:
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
	t = part.get_payload(decode=True)[-raw_len:]
	t = re_html.sub(b'', t)
	t = t.translate(None, bad_char)
	return t[-256:]


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
	>>> test_drop_alternatives(open('test_email/20160916.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170901.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170917.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20170925.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171003.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171003-2.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004.eml').read(), DEBUG)
	multipart/mixed text/plain text/plain
	>>> test_drop_alternatives(open('test_email/20171004-2.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-4.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-5.eml').read(), DEBUG)
	multipart/mixed text/plain text/plain text/plain
	>>> test_drop_alternatives(open('test_email/20171005.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171005-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171011.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018-2.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171020.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171022.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171023.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171025.eml').read(), DEBUG)
	multipart/mixed text/plain
	"""
	print(' '.join([p.get_content_type() for p in drop_alternatives(msg_str, debug).walk()]))


if __name__ == "__main__":
	if version_info.major > 2:
		print(drop_alternatives(TextIOWrapper(stdin.buffer, errors='ignore').read()))
	else:
		print(drop_alternatives(stdin.read()))
