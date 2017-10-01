#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


from __future__ import print_function
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher


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

		for part in eml.walk():
			if (part.get_content_maintype() == "multipart" or
				part.get_content_type() == "message/external-body" or
				part.get_payload() == ""):
				continue
			elif part.get_content_type() == "text/plain":
				texts.append(part.get_payload())
				kept_parts.append(part)
			elif part.get_content_type() == "text/html":
				html_parts.append(part)
			else:
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				for i, t in enumerate(texts):
					if SequenceMatcher(a=h.get_payload(), b=t).real_quick_ratio() < 0.5:
						kept_parts.append(h)
					else:
						del texts[i]
						recompose_msg = True

			if recompose_msg:
				return compose_message(eml, kept_parts)

	return eml


def test_drop_alternatives(msg_str):
	"""
	>>> test_drop_alternatives('Content-Type: text/plain;\\nA')
	text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<p>B</p>')
	multipart/mixed;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<p>A</p>')
	multipart/mixed;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nCoucou\\n'
	... '--\\nContent-Type: text/html;\\n<p>Coucou</p>')
	multipart/mixed;text/plain;
	"""
	for p in drop_alternatives(msg_str).walk():
		print(p.get_content_type(), end=';')
		# print(p.get_payload())
	print('')


if __name__ == "__main__":
	import sys
	if sys.version_info.major > 2:
		from io import TextIOWrapper
		print(drop_alternatives(TextIOWrapper(stdin.buffer, errors='ignore').read()))
	else:
		print(drop_alternatives(sys.stdin.read()))
