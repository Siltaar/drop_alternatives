#!/usr/bin/env python3
# coding: utf-8
# author : Simon Descarpentries
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
		return eml

	new_eml = clone_message(eml)
	flat_eml = [part for part in eml.walk()]
	x_drop_alt = ''

	if 'alternative' not in eml.get_content_subtype():
		flat_eml.pop(0)  # replaced by multipart/mixed

	new_eml, x_drop_alt = recurse_parts(new_eml, flat_eml, x_drop_alt, debug)
	new_eml['x-drop-alt'] = x_drop_alt

	debug and _structure(new_eml)

	return new_eml


def recurse_parts(new_eml, flat_eml, x_drop_alt, debug=0):
	while len(flat_eml) > 0:
		part = flat_eml.pop(0)
		debug and print(part.get_content_type(), end='', file=stderr)

		if 'alternative' in part.get_content_subtype() and len(flat_eml) > 1:
			candidate_txt = flat_eml.pop(0)
			debug and print(' txt '+candidate_txt.get_content_type(), end='', file=stderr)
			candidate_html = flat_eml.pop(0)
			debug and print(' html '+candidate_html.get_content_type(), end='', file=stderr)

			if 'html' in candidate_html.get_content_subtype():
				new_eml.attach(candidate_txt)
				x_drop_alt += 'h'
				debug and print(' keep txt ', file=stderr)
			elif 'related' in candidate_html.get_content_subtype():
				debug and print(' rel -> X ', file=stderr)
				new_eml.attach(candidate_txt)
				sub_part = flat_eml.pop(0)
				x_drop_alt += '.'

				while not sub_part.is_multipart() and len(flat_eml) > 0:  # consume intput
					sub_part = flat_eml.pop(0)
					x_drop_alt += '.'

				if sub_part.is_multipart():
					flat_eml.insert(0, sub_part)
			else:  # unknown configuration
				print('drop_alternative : unkown email configuration', file=stderr)
				new_eml.attach(candidate_txt)  # save parts
				new_eml.attach(candidate_html)  # save parts
		elif 'message' in part.get_content_maintype():
			debug and print(' clne', file=stderr)
			flat_sub_eml = [sub_part for sub_part in part.walk()]
			flat_sub_eml.pop(0)  # replaced by multipart/mixed
			flat_eml = flat_eml[len(flat_sub_eml):]  # consume input
			sub_msg, x_drop_alt = recurse_parts(
				clone_message(part), flat_sub_eml, x_drop_alt, debug)
			new_eml.attach(sub_msg)
		else:
			new_eml.attach(part)
			debug and print('    kept', file=stderr)

	return new_eml, x_drop_alt


def clone_message(eml):
	new_eml = MIMEMultipart(_subtype=eml.get_content_subtype(), boundary=eml.get_boundary())

	for k, v in eml.items():  # `eml` have only headers as its items
		if k not in ["content-length", "content-type", "lines", "status"]:  # unwanted fields
			# Python will set its own Content-Type line in any case
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
