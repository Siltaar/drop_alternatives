#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries - simon /\ acoeuro [] com
# date: 2017 - 2018
# licence: GPLv3

from email.parser import BytesParser
from email.mime.multipart import MIMEMultipart
from email.iterators import _structure	# noqa
from sys import stdin, stderr
from difflib import SequenceMatcher
from re import DOTALL, compile as compile_re


purge_html_re = compile_re(  # match, to remove :
	b'<(sty|(o|w):|scr|tit|[^y]*y\s*:\s*(n|h)).*?</[^>]*'
	# style, o: w:, script, title, display:none / hidden HTML tags, text leaf, partial ending
	b'|<!--.*?-->'  # HTML comments
	b'|<[^>]*'		# all complete HTML tags,  # some may be cut at the end/begining
	b'|&[^;]*;'		# HTML entities
	b'|[\d*]'		# links prefix in converted texts
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


def drop_alternatives(msg_bytes, debug=0):
	eml = BytesParser().parsebytes(msg_bytes)
	debug and _structure(eml)

	if not eml.is_multipart():
		debug and print('not eml.is_multipart()', file=stderr)
		return eml

	x_drop_alt = []
	flat_eml = [[part for part in eml.walk()]]
	new_eml = [clone_message(eml)]

	if not eml.get_content_subtype().startswith('alt'):  # alternative
		flat_eml[0].pop(0)  # replaced by multipart/mixed

	while len(flat_eml) > 0:
		while len(flat_eml[0]) > 0:
			part = flat_eml[0].pop(0)
			debug and print(part.get_content_type(), end='', file=stderr)

			if part.get_content_subtype().startswith('alt') and len(flat_eml[0]) > 1:
				candidate_txt = flat_eml[0].pop(0)
				keep_part(new_eml[0], candidate_txt, x_drop_alt, '', debug)
				debug and print(' txt '+candidate_txt.get_content_type(), end='', file=stderr)

				candidate_htm = flat_eml[0].pop(0)
				debug and print(' htm '+candidate_htm.get_content_type(), end='', file=stderr)
				candidate_htm_subtype = candidate_htm.get_content_subtype()

				if candidate_htm_subtype.startswith('htm'):  # html
					if are_idem_txt(candidate_txt, candidate_htm, debug):
						x_drop_alt.append(candidate_htm_subtype)
					else:
						keep_part(new_eml[0], candidate_htm, x_drop_alt, ' htm diff ', debug)
				elif candidate_htm_subtype.startswith('rel'):  # related
					sub_part = flat_eml[0].pop(0)

					while not sub_part.is_multipart() and len(flat_eml[0]) > 0:
						if sub_part.get_content_subtype().startswith('htm'):
							if are_idem_txt(candidate_txt, sub_part, debug):
								x_drop_alt.append(candidate_htm_subtype)
							else:
								keep_part(
									new_eml[0], sub_part, x_drop_alt, ' rel htm diff ', debug)
						else:
							x_drop_alt.append(sub_part.get_content_type())

						sub_part = flat_eml[0].pop(0)  # consume intput

					if sub_part.is_multipart():
						flat_eml[0].insert(0, sub_part)
				else:  # unknown configuration yet
					keep_part(new_eml[0], candidate_htm, x_drop_alt, ' new case ? ', debug)
			elif part.get_content_maintype().startswith('me'):  # message
				debug and print(' clne', file=stderr)
				flat_sub_eml = [sub_part for sub_part in part.walk()]
				flat_sub_eml.pop(0)  # replaced by multipart/mixed
				flat_eml[0] = flat_eml[0][len(flat_sub_eml):]  # consume input
				flat_eml.insert(0, flat_sub_eml)
				new_eml.insert(0, clone_message(part))
			else:
				new_eml[0].attach(part)
				debug and print('	 kept', file=stderr)

		if len(new_eml) > 1:
			new_eml[1].attach(new_eml[0])
			new_eml.pop(0)

		flat_eml.pop(0)

	new_eml[0]['x-drop-alt'] = ', '.join(x_drop_alt)
	debug and _structure(new_eml[0])
	return new_eml[0]


def keep_part(new_eml, part, x_drop_alt, why, debug=0):
	debug and print(why, file=stderr)
	x_drop_alt.append(why)
	new_eml.attach(part)


def are_idem_txt(part_txt, part_htm, debug=0):
	txt_1, txt_2 = get_txt(part_txt, 3000)
	htm_1, htm_2 = get_txt(part_htm, 30000)
	s_1, s_2 = min(len(htm_1), len(txt_1)), min(len(htm_2), len(txt_2))
	idem_ratio_1 = SequenceMatcher(a=htm_1[:s_1], b=txt_1[:s_1]).quick_ratio()
	idem_ratio_2 = SequenceMatcher(a=htm_2[-s_2:], b=txt_2[-s_2:]).quick_ratio()
	idem_ratio = (idem_ratio_1 + idem_ratio_2) / 2

	if debug:
		from shutil import get_terminal_size
		ir = ' '+color_ratio(idem_ratio)
		rows, cols = get_terminal_size()
		PUT_txt = int(cols) - 8
		PUT_htm = int(cols) - 2

		def put(string, postfix, size):
			print(string[:size].ljust(size, '.') + postfix, file=stderr)

		# if True:
		if idem_ratio_1 < LIM:
			# put((i and B or G) + str(h_t_1),	W + ' <H', PUT_htm - 1)
			put('\n' + str(htm_1),	W + ' <H', PUT_htm - 1)
			put(str(txt_1), ' T '+color_ratio(idem_ratio_1)+ir, PUT_txt)
		# if True:
		if idem_ratio_2 < LIM:
			# put((i and B or G) + str(h_t_2), W + ' H>', PUT_htm)
			put('\n' + str(htm_2), W + ' H>', PUT_htm)
			put(str(txt_2), ' T '+color_ratio(idem_ratio_2)+ir, PUT_txt)

	return idem_ratio_1 > BON or idem_ratio_2 > BON or idem_ratio > LIM


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


def clone_message(eml):
	new_eml = MIMEMultipart(_subtype=eml.get_content_subtype(), boundary=eml.get_boundary())

	for k, v in eml.items():  # `eml` have only headers as its items
		if k not in ["content-length", "content-type", "lines", "status"]:  # unwanted fields
			# Python will set its own Content-Type line in any case
			# Content-Length would change if a part is dropped
			# Lines idem
			# Status unknown
			new_eml[k] = v

	new_eml.preamble = eml.preamble
	new_eml.epilogue = eml.epilogue

	if len(eml.defects):
		new_eml['x-python-parsing-defects'] = str(eml.defects)

	return new_eml


DEBUG = 1


if __name__ == "__main__":
	if DEBUG:
		drop_alternatives(stdin.buffer.raw.read(), DEBUG)
	else:
		print(drop_alternatives(stdin.buffer.raw.read()))
