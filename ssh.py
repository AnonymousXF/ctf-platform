# -*- coding: utf-8 -*-
import pexpect
import os
import time
import getpass

logFileId = open("logfile.txt", 'w+')
def ssh_detection(ip, user, passwd):
    try:
    	ssh = pexpect.spawn('ssh '+user+'@'+ip+" echo hello")
    	ssh.logfile = logFileId
        index = ssh.expect(['password: ', 'continue connecting (yes/no)?', 'hello'])
        if index == 0 :
            ssh.sendline(passwd)
            index = ssh.expect('hello')
            if index == 0:
            	print "未配置ssh公私钥"
            ssh.close(force=True)
            return 2
        elif index == 1:
            ssh.sendline('yes\n')
            index = ssh.expect('password: ')
            print "未配置ssh公私钥"
            ssh.close(force=True)
            return 2
        elif index == 2:
        	print "已配置ssh公私钥"
        	ssh.close(force=True)
        	return 1
    except:
    	print "ERROR"
        return 0

def ssh_configure(ip, user, passwd):
	print "开始配置公私钥"
	path = os.getcwd()
	#if path.split('/')[1] == 'home':
	#	rsa_path = '/home/'+path.split('/')[2]+'/.ssh/id_rsa.pub'
	#else:
	#	name = raw_input("请输入当前主机的用户名：")
	#	rsa_path = '/home/'+name+'/.ssh/id_rsa.pub'
	rsa_path = '/root/.ssh/id_rsa.pub'
	if not os.path.exists(rsa_path):
		try:
			keygen = pexpect.spawn("ssh-keygen")
			keygen.logfile = logFileId
			index = keygen.expect("Enter file in which to save the key")
			keygen.sendline('')
			index = keygen.expect("Enter passphrase ")
			keygen.sendline('')
			index = keygen.expect("Enter same passphrase again")
			keygen.sendline('')
			time.sleep(1)
			keygen.close(force=True)
		except:
			print "ERROR ssh-keygen"
	else:
		pass
	try:
		ssh = pexpect.spawn("ssh-copy-id -i "+rsa_path+" "+user+"@"+ip)
		ssh.logfile = logFileId
		time.sleep(10)
		index = ssh.expect("password")
		ssh.sendline(passwd)
		time.sleep(1)
		ssh.close(force=True)
	except:
		print "ERROR ssh-copy-id"
	try:
		ssh = pexpect.spawn('ssh '+user+'@'+ip+' echo hello')
		ssh.logfile = logFileId
		index = ssh.expect(['password', 'hello'])
		if index == 0:
			# ssh.close(force=True)
			pexpect.run("eval 'ssh-agent -s'")
	    	pexpect.run("ssh-add")
	    	ssh.close(force=True)
	    	ssh = pexpect.spawn('ssh '+user+'@'+ip+" echo hello")
	    	ssh.logfile = logFileId
	    	index = ssh.expect('hello')
	    	if index == 0:
	    		print "ssh公私钥配置成功"
	    		return True
		elif index == 1:
			print "ssh公私钥配置成功"
			return True
	except:
		print "配置失败"
        return False

def vmachine_detection(ip, user, passwd):
	try:
		ssh = pexpect.spawn('ssh '+user+'@'+ip+" virsh -c qemu:///system")
		ssh.logfile = logFileId
		index = ssh.expect(['Welcome to virsh','virsh: command not found'])
		if index == 0:
			ssh.close(force=True)
			return True
		elif index == 1:
			ssh.close(force=True)
			return False
	except:
		ssh.close(force=True)
        return False

if __name__=='__main__':
	ip = raw_input("请输入远程ssh连接的IP 地址：")
	user = raw_input("登录名：")
	passwd = getpass.getpass("登录密码：")
	index = ssh_detection(ip,user,passwd)
	if index == 0:
		print "ssh连接有问题，请检查用户名密码输入是否正确，以及远程主机是否允许ssh连接"
		exit()
	elif index == 2:
		index = ssh_configure(ip,user,passwd)
		if not index:
			print "ssh公私钥配置失败,请尝试手动配置"
			exit()
	print ".......ssh检查pass"
	if not vmachine_detection(ip,user,passwd):
		print "远程主机未配置好虚拟机的相关环境，请在远程主机上配值好相关环境后再运行。"
		exit()
	print ".......虚拟机环境检查pass"
