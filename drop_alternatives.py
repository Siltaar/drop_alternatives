#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-09
# licence: GPLv3

"""
Copyright: 2017 Simon Descarpentries
Copyright: 2010-2012 Rogério Theodoro de Brito

`drop_alternatives.py` is a simple Python script for those who hate emails in
HTML and who prefer their inbox to have as many messages in pure text as
feasible. This script is generally meant to be run as a filter with procmail
FDM or some other mail delivery agent.

It tries to be moderately conservative and only act when things are
moderately safe:

* If the message is `multipart` and has a `text/plain` and a `text/html`
  part, keep the `text/plain` part only.

* In all other cases keep the message intact.
"""

import email
import email.message


def compose_message(orig, body):
	"""
	Create new message with headers from `orig` and body from `body`.

	* `orig`: The original message.
	* `body`: The body that we want the new message to have.
	* Returns a new message.

	`compose_message` creates a new message with most of the fields from
	`orig`, with fields from `body` (if any) and with the payload of
	`body`. The fields excluded from `orig` are the following:

	* `content-length`
	* `content-type`
	* `lines`
	* `status`
	"""
	wanted = email.message.Message()
	wanted.set_payload(body.get_payload())

	unwanted_fields = ["content-length", "content-type", "lines", "status"]

	# The dictionaries `orig` and `body` have only headers as their items.
	for field in unwanted_fields:
		del orig[field]

	for k, v in orig.items():
		wanted[k] = v
	for k, v in body.items():
		wanted[k] = v

	return wanted


def drop_alternatives(msg):
	"""
	Given an RFC-2822 message `msg`, generate its 'sanitized' version.

	* `msg`: The message to be sanitized.
	* Returns a sanitized version of `msg`.

	`drop_HTML_part` tries to be moderately conservative and only act when things
	are moderately safe:

	* If the message is multipart and has a `text/plain` and a `text/html`
		part, keep the `text/plain` part only.

	* In all other cases keep the message intact.
	"""
	if not msg.is_multipart():
		return msg

	# 'composition' is a bitmask containing the kind of the parts
	TEXTPLAIN = 1  # text/plain
	TEXTHTML = 2  # text/html
	MISCPARTS = 4  # anything else

	composition = 0
	text_taken = False

	for part in msg.walk():
		if (part.get_content_maintype() == "multipart" or
			part.get_content_type() == "message/external-body" or
			part.get_payload() == ""):
			continue
		elif part.get_content_type() == "text/plain":
			if not text_taken:
				text_taken = True
				body = part
				composition |= TEXTPLAIN
			else: # if we are seeing a second text/plain part, stop throwing things
				composition |= MISCPARTS
				break
		elif part.get_content_type() == "text/html":
			composition |= TEXTHTML
		else:
			composition |= MISCPARTS

	if (composition & TEXTPLAIN) != 0 and (composition & MISCPARTS) == 0:
		return compose_message(msg, body)
	else:
		return msg


if __name__ == "__main__":
	import sys
	print(drop_alternatives(email.message_from_file(sys.stdin)).as_string())
