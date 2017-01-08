# -*- coding: utf-8 -*-
import bcrypt
import oath
import re

		
def check_Password(pwd):
    lenOK=len(pwd)>=8
    upperOK=re.compile('[A-Z]+').findall(pwd)    #�ж��Ƿ������д��ĸ
    lowerOK=re.compile('[a-z]+').findall(pwd)    #�ж��Ƿ����Сд��ĸ
    numOK=re.compile('[0-9]+').findall(pwd)      #�ж��Ƿ��������
    symbolOK=re.compile('([^a-z0-9A-Z])+').findall(pwd)      #�ж��Ƿ��������
    return (lenOK and numOK and (upperOK or lowerOK or symbolOK))

def create_password(pw):
    return bcrypt.hashpw(pw, bcrypt.gensalt())

def verify_password(user, pw):
    return bcrypt.hashpw(pw.encode(), user.password.encode()) == user.password.encode()