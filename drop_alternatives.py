#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


import email
from email.mime.multipart import MIMEMultipart


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


def drop_alternatives(msg):
	if msg.is_multipart():
		no_html_parts = []
		text_parts = []
		html_parts = []

		for part in msg.walk():
			if (part.get_content_maintype() == "multipart" or
				part.get_content_type() == "message/external-body" or
				part.get_payload() == ""):
				no_html_parts.append(part)
			elif part.get_content_type() == "text/plain":
				text_parts.append(part)
				no_html_parts.append(part)
			elif part.get_content_type() == "text/html":
				html_parts.append(part)
			else:
				no_html_parts.append(part)

		if (html_parts and len(text_parts) >= len(html_parts) and
			sum([len(a.get_payload()) for a in html_parts]) <
				10 * sum([len(b.get_payload()) for b in text_parts])):
			return compose_message(msg, no_html_parts)

	return msg


if __name__ == "__main__":
	import sys
	print(drop_alternatives(email.message_from_file(sys.stdin)))
