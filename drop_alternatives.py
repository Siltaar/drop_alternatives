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
	b'<(tit|sty|scr|.:|[^y]*y:n).*?</[^>]*|<!--.*?-->|<[^>]*|[\d*]|&[^;]*;|[^\s\n\r<]{25,}',
	# match and so remove :
	# - title, style, script, o:… / w:…, display:none HTML tags and their text leafs
	# - all HTML tags,  # even if cut at the begining
	# - HTML comments
	# - links prefix in converted texts
	# - HTML entities
	# - chunks of symbols without spaces too big to be words (such as URL)
	DOTALL)
bad_char = b' \t\n\r\xc2\xa0\'#->=:*]['  # exist: \v Vertical tab ; \f From feed
W  = '\033[0m'  # white (normal)
G  = '\033[1;30m' # grey
R  = '\033[1;31m' # bold red
Y  = '\033[1;33m' # bold yellow
B  = '\033[1;37m' # bold white
LEN = 280
LIM = .82
BON = .91

def drop_alternatives(msg_str, debug=0):
	eml = Parser().parsestr(msg_str)

	if eml.is_multipart():
		kept_parts = []
		html_parts = []
		texts = []

		for part in eml.walk():
			# debug and print('part content_type '+part.get_content_type(), file=stderr)

			if ("multipart" in part.get_content_maintype() or
				"message" in part.get_content_type()):
				continue
			elif 'html' in part.get_content_type():
				html_parts.append(part)
				# debug and print('got HTML', file=stderr)
			elif 'plain' in part.get_content_type():
				kept_parts.append(part)
				texts.append(get_txt(part, 2300))
				# debug and print('got TEXT', file=stderr)
			else:
				kept_parts.append(part)
				# debug and print('kept part '+part.get_content_type(), file=stderr)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt_1, h_txt_2 = get_txt(h, 40000)
				len_h_txt_1 = len(h_txt_1)
				len_h_txt_2 = len(h_txt_2)
				save_html = True

				for i, t in enumerate(texts):
					t_1, t_2 = t
					s_1 = min(len_h_txt_1, len(t_1))
					s_2 = min(len_h_txt_2, len(t_2))
					idem_ratio_1 = SequenceMatcher(a=h_txt_1[:s_1], b=t_1[:s_1]).quick_ratio()
					idem_ratio_2 = SequenceMatcher(a=h_txt_2[-s_2:], b=t_2[-s_2:]).quick_ratio()
					idem_ratio = (idem_ratio_1 + idem_ratio_2) / 2

					if debug:
						ir = ' '+color_ratio(idem_ratio)

						if idem_ratio_1 < LIM:
							print(i and B or G + str(h_txt_1[:LEN]) + W + ' H 1', file=stderr)
							print(str(t_1[:LEN])+' T '+color_ratio(idem_ratio_1)+ir,file=stderr)
						if idem_ratio_2 < LIM:
							print(i and B or G + str(h_txt_2[-LEN:]) + W + ' H 2', file=stderr)
							print(str(t_2[:LEN])+' T '+color_ratio(idem_ratio_2)+ir,file=stderr)

					if idem_ratio_1 > BON or idem_ratio_2 > BON or idem_ratio > LIM:
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
	t = part.get_payload(decode=True)
	t_start = t[:raw_len]
	t_end = t[-raw_len:]
	t_start = re_html.sub(b'', t_start)
	t_start = t_start.translate(None, bad_char)
	t_end = re_html.sub(b'', t_end)
	t_end = t_end.translate(None, bad_char)
	return t_start[:LEN], t_end[-LEN:]  # Python 2 ratio() changes its behavior after 199c


def color_ratio(ratio):
	C = ratio < LIM and R or ratio < BON and Y or W
	return str(C + str(int(ratio*100)) + W)


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
	multipart/mixed text/plain application/octet-stream
	>>> test_drop_alternatives(open('test_email/20171004-4.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171004-5.eml').read(), DEBUG)
	multipart/mixed text/plain text/plain text/plain
	>>> test_drop_alternatives(open('test_email/20171005.eml').read(), DEBUG)
	multipart/mixed text/plain image/png
	>>> test_drop_alternatives(open('test_email/20171005-3.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171011.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20171018-2.eml').read(), DEBUG)
	multipart/mixed text/plain application/pdf
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
	>>> test_drop_alternatives(open('test_email/20171109.eml').read(), DEBUG)
	multipart/mixed text/plain image/png
	>>> test_drop_alternatives(open('test_email/20180312.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20180314.eml').read(), DEBUG)
	multipart/mixed text/plain
	>>> test_drop_alternatives(open('test_email/20180315.eml').read(), DEBUG)
	multipart/mixed text/plain
	"""
	print(' '.join([p.get_content_type() for p in drop_alternatives(msg_str, debug).walk()]))


if version_info.major > 2:  # In Python 3: str is the new unicode
    unicode = str

if __name__ == "__main__":
	if version_info.major > 2:
		print(drop_alternatives(TextIOWrapper(stdin.buffer, errors='ignore').read()))
	else:
		print(drop_alternatives(stdin.read()))
