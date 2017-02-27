# -*- coding: utf-8 -*-
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
    send_email(team_email, "欢迎来到 {}!".format(config.ctf_name),
"""Hello, 感谢你的注册 {}! 在你开始答题前,
你必须先在主页面，输入下列验证码，进行邮箱验证:

{}

一旦你完成了这些, 你的帐号将会被激活, 然后就可以加入答题页面了. 如果你有任何问题, 欢迎随时联系管理员，管理员邮箱hustctf@163.com!

如果你没有进行注册, 请忽略该邮件.
""".format(config.ctf_name, confirmation_key))

def is_valid_email(email):
    return not email.strip().lower().endswith(config.disallowed_domain)