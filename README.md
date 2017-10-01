`drop_alternatives.py` is a simple Python script for those who hate emails in
HTML and who prefer their inbox to have as many messages in pure text as
feasible. Given an RFC-2822 message message, it generates its 'sanitized'
version.

This script is generally meant to be run as a filter with procmail,
[FDM](https://github.com/nicm/fdm) or some other mail delivery agent.

It tries to be moderately conservative and only act when things are
moderately safe:

* If the message is `multipart` and has a `text/plain` and a `text/html`
  part, keep the `text/plain` part only.
* In all other cases keep the message intact.

### `fdm.conf` example :

`match all action rewrite "python2 -SE drop_alternatives.py" continue`

***

Copyright: 2010-2012 @rbrito from a StackExchange [thread](https://codereview.stackexchange.com/questions/12967/script-to-drop-html-part-of-multipart-mixed-e-mails/12970) [GitHub account](https://github.com/rbrito) \
Copyright: 2017 Simon Descarpentries
