#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries - simon /\ acoeuro [] com
# date: 2017 - 2018
# licence: GPLv3

from email.parser import BytesParser
from email.mime.multipart import MIMEMultipart
from email.iterators import _structure
from sys import stdin, stderr


def drop_alternatives(msg_bytes, debug=0):
	eml = BytesParser().parsebytes(msg_bytes)
	debug and _structure(eml)

	if not eml.is_multipart():
		debug and print('not eml.is_multipart()', file=stderr)
		return eml

	x_drop_alt = []
	flat_eml = [[part for part in eml.walk()]]
	new_eml = [clone_message(eml)]

	if 'alt' != eml.get_content_subtype()[:3]:  # alternative
		flat_eml[0].pop(0)  # replaced by multipart/mixed

	while len(flat_eml) > 0:
		while len(flat_eml[0]) > 0:
			part = flat_eml[0].pop(0)
			debug and print(part.get_content_type(), end='', file=stderr)

			if 'alt' == part.get_content_subtype()[:3] and len(flat_eml[0]) > 1:
				candidate_txt = flat_eml[0].pop(0)
				debug and print(' txt '+candidate_txt.get_content_type(), end='', file=stderr)
				candidate_html = flat_eml[0].pop(0)
				debug and print(' htm '+candidate_html.get_content_type(), end='', file=stderr)
				candidate_html_content_type = candidate_html.get_content_subtype()[:3]

				if 'htm' == candidate_html_content_type:  # html
					new_eml[0].attach(candidate_txt)
					debug and print(' keep txt ', file=stderr)
					x_drop_alt.append(candidate_html_content_type)
				elif 'rel' == candidate_html_content_type:  # related
					x_drop_alt.append(candidate_html_content_type)
					debug and print(' drop rel ', file=stderr)
					new_eml[0].attach(candidate_txt)
					sub_part = flat_eml[0].pop(0)

					while not sub_part.is_multipart() and len(flat_eml[0]) > 0:
						x_drop_alt.append(sub_part.get_content_type())
						sub_part = flat_eml[0].pop(0)  # consume intput

					if sub_part.is_multipart():
						flat_eml[0].insert(0, sub_part)
				else:  # unknown configuration yet
					debug and print('unknown email configuration', file=stderr)
					x_drop_alt.append('unknown alternative configuration')
					new_eml[0].attach(candidate_txt)  # save parts
					new_eml[0].attach(candidate_html)  # save parts
			elif 'me' == part.get_content_maintype()[:2]:  # message
				debug and print(' clne', file=stderr)
				flat_sub_eml = [sub_part for sub_part in part.walk()]
				flat_sub_eml.pop(0)  # replaced by multipart/mixed
				flat_eml[0] = flat_eml[0][len(flat_sub_eml):]  # consume input
				flat_eml.insert(0, flat_sub_eml)
				new_eml.insert(0, clone_message(part))
			else:
				new_eml[0].attach(part)
				debug and print('    kept', file=stderr)

		if len(new_eml) > 1:
			new_eml[1].attach(new_eml[0])
			new_eml.pop(0)

		flat_eml.pop(0)

	new_eml[0]['x-drop-alt'] = ', '.join(x_drop_alt)
	debug and _structure(new_eml[0])
	return new_eml[0]


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


DEBUG = 0


if __name__ == "__main__":
	if DEBUG:
		drop_alternatives(stdin.buffer.raw.read(), DEBUG)
	else:
		print(drop_alternatives(stdin.buffer.raw.read()))
