#!/usr/bin/python3

import smtplib
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from config.mailcfg import gmail

gmail_user = gmail['user']
gmail_pwd = gmail['passwd']
FROM = gmail['from']

def send_message(to, subject, text):
	#Prepare actual email
	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (FROM, to, subject, text)

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.login(gmail_user, gmail_pwd)
	server.sendmail(FROM, to, message)
	server.close()
