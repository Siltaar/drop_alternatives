#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from __future__ import print_function
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
from sys import stdin, stderr, version_info
from re import DOTALL, compile as compile_re
from os import popen


purge_html_re = compile_re(  # match, to remove :
	b'<(sty|(o|w):|scr|tit|[^y]*y\s*:\s*(n|h)).*?</[^>]*'
	# style, o: w:, script, title, display:none / hidden HTML tags, text leaf, partial ending
	b'|<!--.*?-->'  # HTML comments
	b'|<[^>]*'      # all complete HTML tags,  # some may be cut at the end/begining
	b'|&[^;]*;'     # HTML entities
	b'|[\d*]'       # links prefix in converted texts
	b'|[^\s<\xc2\xa0]{25,}',  # - chunks of symbols without spaces too big to be words (as URL)
	DOTALL)
bad_chars = b' >\n\xc2\xa0.,@#-=:*][+_()/|\'\t\r\f\v\\'
W = '\033[0m'  # white (normal)
G = '\033[1;30m'  # grey
R = '\033[1;31m'  # bold red
Y = '\033[1;33m'  # bold yellow
B = '\033[1;37m'  # bold white
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
				texts.append(get_txt(part, 3000))
				# debug and print('got TEXT', file=stderr)
			else:
				kept_parts.append(part)
				# debug and print('kept part '+part.get_content_type(), file=stderr)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_t_1, h_t_2 = get_txt(h, 30000)
				s_h_t_1, s_h_t_2 = len(h_t_1), len(h_t_2)
				save_html = True

				for i, (t_1, t_2) in enumerate(texts):
					s_1, s_2 = min(s_h_t_1, len(t_1)), min(s_h_t_2, len(t_2))
					idem_ratio_1 = SequenceMatcher(a=h_t_1[:s_1], b=t_1[:s_1]).quick_ratio()
					idem_ratio_2 = SequenceMatcher(a=h_t_2[-s_2:], b=t_2[-s_2:]).quick_ratio()
					idem_ratio = (idem_ratio_1 + idem_ratio_2) / 2

					if debug:
						ir = ' '+color_ratio(idem_ratio)
						rows, columns = popen('stty size', 'r').read().split()
						PUT = int(columns) - 8

						def put(string, postfix, size):
							print(string[:size].ljust(size) + postfix, file=stderr)

						# if True:
						if idem_ratio_1 < LIM:
							put((i and B or G) + str(h_t_1),  W + ' <H', PUT)
							put(str(t_1), ' T '+color_ratio(idem_ratio_1)+ir, PUT)
						# if True:
						if idem_ratio_2 < LIM:
							put((i and B or G) + str(h_t_2), W + ' H>', PUT)
							put(str(t_2), ' T '+color_ratio(idem_ratio_2)+ir, PUT)

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


def get_txt(part, raw_len, bad_chars=bad_chars):
	t = part.get_payload(decode=True)
	# raw_len < 20000 and print('raw TXT '+t, file=stderr)
	t_start = t[:raw_len]
	t_end = t[-raw_len:]
	t_start = purge_html_re.sub(b'', t_start)
	# raw_len < 20000 and print(R+'apr purge '+W+t_start, file=stderr)
	t_start = t_start.translate(None, bad_chars)
	t_end = purge_html_re.sub(b'', t_end)
	t_end = t_end.translate(None, bad_chars)
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


if __name__ == "__main__":
	if version_info.major > 2:
		from io import TextIOWrapper
		print(drop_alternatives(TextIOWrapper(stdin.buffer, errors='ignore').read()))
	else:
		print(drop_alternatives(stdin.read()))
