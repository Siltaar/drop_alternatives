#!/usr/bin/python3
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3


from __future__ import print_function
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
from lxml import html
import sys


DEBUG = False


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
		debug(' ')
		kept_parts = []
		html_parts = []
		texts = []

		for part in eml.walk():
			if (part.get_content_maintype() == "multipart" or
				part.get_content_type() == "message/external-body" or
				part.get_payload() == ""):
				continue
			elif part.get_content_type() == "text/plain":
				kept_parts.append(part)
				texts.append(part.get_payload(decode=True))
			elif part.get_content_type() == "text/html":
				html_parts.append(part)
			else:
				kept_parts.append(part)

		if html_parts:
			recompose_msg = False

			for h in html_parts:
				h_txt = html.fromstring(str(h.get_payload(decode=True)))

				for tag in h_txt.cssselect('style'):
					tag.drop_tree()
				for tag in h_txt.cssselect('script'):
					tag.drop_tree()

				h_txt = str(h_txt.text_content())
				h_txt = h_txt.replace('\\n', '')
				h_txt = h_txt.replace('\\t', '')
				h_txt = h_txt.replace('\t', '')
				h_txt = h_txt.replace('  ', '')
				h_txt = h_txt.replace('\n\n', '')

				save_html = True

				for i, t in enumerate(texts):
					diff_ratio = SequenceMatcher(a=h_txt, b=t).real_quick_ratio()
					debug(str(h_txt)+' '+str(t)+' '+str(diff_ratio))

					if diff_ratio > 0.50:
						save_html = False
						recompose_msg = True
						del texts[i]  # avoid comparing again with this text

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
	... '--\\nContent-Type: text/plain;\\nAAA\\n'
	... '--\\nContent-Type: text/html;\\n<style>body{color}</style><body>AAA</body>')
	multipart/mixed;text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/html;\\n<html><style>a{color red;}</style>BBBBBBBBB')
	multipart/mixed;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nBBBB\\n'
	... '--\\nContent-Type: text/html;\\n<style>a{color}</style>BBBB')
	multipart/mixed;text/plain;text/plain;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nB\\n'
	... '--\\nContent-Type: text/html;\\n<p>C</p>')
	multipart/mixed;text/plain;text/plain;text/html;
	>>> test_drop_alternatives('Content-Type: multipart/mixed; boundary=""\\n'
	... '--\\nContent-Type: text/plain;\\nA\\n'
	... '--\\nContent-Type: text/plain;\\nBBBB\\n'
	... '--\\nContent-Type: text/html;\\n<html><style>a{color}</style>BBBB</html>\\n'
	... '--\\nContent-Type: text/html;\\n<style>body{color}</style><body>CCCCCCCCC</body>')
	multipart/mixed;text/plain;text/plain;text/html;
	"""
	for p in drop_alternatives(msg_str).walk():
		print(p.get_content_type(), end=';')
		# debug(str(p.get_payload()))
	print('')


def debug(s):
    if DEBUG:
        print(s, file=sys.stderr)


if __name__ == "__main__":
	from io import TextIOWrapper
	print(drop_alternatives(TextIOWrapper(sys.stdin.buffer, errors='ignore').read()))
