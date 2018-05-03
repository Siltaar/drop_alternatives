#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries - simon /\ acoeuro [] com
# date: 2017 - 2018
# licence: GPLv3

from email.parser import BytesParser
from email.mime.multipart import MIMEMultipart
from email.iterators import _structure	# noqa
from sys import stdin, stderr, argv
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
	# debug and _structure(eml)

	if not eml.is_multipart():
		debug and print('not multipart', file=stderr)
		return eml

	x_drop_alt = []
	flat_eml = [[part for part in eml.walk()]]

	if not len([part for part in eml.walk() if 'htm' in part.get_content_subtype()]):
		debug and print('no HTML to drop', file=stderr)
		return eml

	flat_eml[0].reverse()
	new_eml = [clone_message(eml)]

	if 'alt' not in eml.get_content_subtype():  # alternative
		flat_eml[0].pop()  # replaced by multipart/mixed

	while len(flat_eml) > 0:
		while len(flat_eml[-1]) > 0:
			part = flat_eml[-1].pop()
			debug and print(part.get_content_type(), end=' ', file=stderr)
			part_content_type = part.get_content_type()

			if 'alt' in part_content_type and len(flat_eml[-1]) > 1:  # alternative
				candidate_txt = flat_eml[-1].pop()
				new_eml[-1].attach(candidate_txt)
				debug and print('txt '+candidate_txt.get_content_type(), end=' ', file=stderr)

				candidate_htm = flat_eml[-1].pop()
				debug and print('htm '+candidate_htm.get_content_type(), end=' ', file=stderr)
				candidate_htm_subtype = candidate_htm.get_content_subtype()

				if 'htm' in candidate_htm_subtype:  # html
					if are_idem_txt(candidate_txt, candidate_htm, debug):
						x_drop_alt.append(candidate_htm_subtype)
					else:
						new_eml[-1].attach(candidate_htm)
						debug and print('htm diff', end=' ', file=stderr)
				elif 'rel' in candidate_htm_subtype:  # related
					sub_part = flat_eml[-1].pop()

					while not sub_part.is_multipart() and len(flat_eml[-1]) > 0:
						if 'htm' in sub_part.get_content_subtype():
							if are_idem_txt(candidate_txt, sub_part, debug):
								x_drop_alt.append(sub_part.get_content_subtype())
							else:
								new_eml[-1].attach(sub_part)
								debug and print('rel htm diff', end=' ', file=stderr)
						else:
							x_drop_alt.append(sub_part.get_content_type())

						sub_part = flat_eml[-1].pop()  # consume intput

					if sub_part.is_multipart():
						flat_eml[-1].append(sub_part)
				else:  # unknown configuration yet
					new_eml[-1].attach(candidate_htm)
					debug and print('new configuration ?', end=' ', file=stderr)
			elif 'me' in part_content_type:  # message
				debug and print(' clne', file=stderr)
				flat_sub_eml = [sub_part for sub_part in part.walk()]
				flat_sub_eml.reverse()
				flat_sub_eml.pop()  # replaced by multipart/mixed
				flat_eml[-1] = flat_eml[-1][:-len(flat_sub_eml)]  # consume input
				flat_eml.append(flat_sub_eml)
				new_eml.append(clone_message(part))
			elif 'rel' in part_content_type:  # related
				debug and print('drop rel', file=stderr)
			else:
				new_eml[-1].attach(part)
				debug and print('	 kept', file=stderr)

		if len(new_eml) > 1:
			new_eml[-2].attach(new_eml[-1])
			new_eml.pop()

		flat_eml.pop()

	if len(x_drop_alt):
		new_eml[0]['x-drop-alt'] = ', '.join(x_drop_alt)
		# debug and _structure(new_eml[0])
		return new_eml[0]
	else:
		return eml


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
		cols, rows = get_terminal_size()
		PUT_txt = int(cols) - 8
		PUT_htm = int(cols) - 7

		def put(string, postfix, size):
			print(string[:size].ljust(size, '.') + postfix, file=stderr)

		if idem_ratio_1 < LIM:  # or True:
			put('\n' + str(htm_1, errors='replace'), W + ' <H', PUT_htm - 1)
			put(str(txt_1, errors='replace'), ' T '+color_ratio(idem_ratio_1)+ir, PUT_txt)
		if idem_ratio_2 < LIM:  # or True:
			put('\n' + str(htm_2, errors='replace'), W + ' H>', PUT_htm)
			put(str(txt_2, errors='replace'), ' T '+color_ratio(idem_ratio_2)+ir, PUT_txt)

	return idem_ratio_1 > BON or idem_ratio_2 > BON or idem_ratio > LIM


def get_txt(part, raw_len, bad_chars=bad_chars):
	t = part.get_payload(decode=True)
	t_start = t[:raw_len]
	t_end = t[-raw_len:]
	t_start = purge_html_re.sub(b'', t_start)
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
			# Python will set its own Content-Type and Content-Length lines in any case
			# Lines may change anyway
			# What is Status ?
			new_eml[k] = v

	new_eml.preamble = eml.preamble
	new_eml.epilogue = eml.epilogue

	if len(eml.defects):
		new_eml['x-python-parsing-defects'] = str(eml.defects)

	return new_eml


if __name__ == "__main__":
	DEBUG = 0

	for i, arg in enumerate(argv):
		if i == 0:  # 1st arg of argv is the program name
			continue
		elif '--debug' in arg:
			DEBUG = 1

	if DEBUG:
		drop_alternatives(stdin.buffer.raw.read(), DEBUG)
	else:
		input_eml = stdin.buffer.raw.read()
		output_eml = drop_alternatives(input_eml)
		str_eml = str(output_eml.as_bytes(), errors='replace')
		print(str_eml, end='')
