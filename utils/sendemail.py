import config
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(to, subject, text):
	msg = MIMEText(text, 'plain', 'utf-8')
	msg['From'] = _format_addr('<%s>' % config.email_sender)
	msg['To'] = _format_addr('<%s>' % to)
	msg['Subject'] = Header(subject, 'utf-8').encode()

	server = smtplib.SMTP(config.email_host, 25)
	#server.set_debuglevel(1)
	server.login(config.email_sender, config.email_pass)
	server.sendmail(config.email_sender, [to], msg.as_string())
	server.quit()

def send_confirmation_email(team_email, confirmation_key):
    send_email(team_email, "Welcome to {}!".format(config.ctf_name),
"""Hello, and thanks for registering for {}! Before you can start solving problems,
you must confirm your email by entering this code into the team dashboard:

{}

Once you've done that, your account will be enabled, and you will be able to access
the challenges. If you have any trouble, feel free to contact an organizer!

If you didn't register an account, then you can disregard this email.
""".format(config.ctf_name, confirmation_key))

def is_valid_email(email):
    return not email.strip().lower().endswith(config.disallowed_domain)