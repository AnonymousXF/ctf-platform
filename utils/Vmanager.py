#-*-coding:utf-8-*-
import os
import sys
import libvirt
from xml.dom import minidom
from flask import current_app

def createConnection(address):
	try:
		conn = libvirt.open(address)
		current_app.logger.info("connect server success.")
		return conn
	except Exception, e:
		current_app.logger.error(e)
		return False

def closeConnection(conn):
	try:
		conn.close()
		current_app.logger.info("close connection with server success.")
		return True
	except Exception, e:
		current_app.logger.error(e)
		return False

def getalldomains(conn):
	domains = conn.listAllDomains()
	return domains

# def getConnInfo(conn):
# 	print "***********Host info ************"
# 	print "Hostname: "+conn.getHostname()
# 	print "FreeMemory: "+str(conn.getFreeMemory())
# 	print "Type: "+conn.getType()
# 	print "URI: "+conn.getURI()+'\n'

def getDomInfoByName(conn, name):
	myDom = conn.lookupByName(name)
	return str(myDom.maxMemory()/1024),str(myDom.info()[3]),str(myDom.state(0)[0])

def startDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		if myDom.state(0)[0]==5:
			myDom.create()
			current_app.logger.info("start vmachine "+name+" success.")
		return True
	except Exception, e:
		current_app.logger.error(e)
		return False

def suspendDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.suspend()
		current_app.logger.info("suspend vmachine "+name+" success.")
		return True
	except Exception, e:
		current_app.logger.error(e)
		return False

def resumeDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.resume()
		current_app.logger.info("resume vmachine "+name+" success.")
		return True
	except Exception, e:
		current_app.logger.error(e)
		return False

def destroyDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.destroy()
		current_app.logger.info("destory vmachine "+name+" success.")
		return True
	except Exception, e:
		current_app.logger.error(e)
		return False

def modify_cpu(address, conn, name, cpuNum, xml):
	ssh = address.split("//")[1].split("/")[0]
	cwd = os.getcwd()
	cwd = cwd+'/'
	try:
		# 将远程主机的xml文件复制到当前目录下。
		os.system("scp "+ssh+":"+xml+name+".xml "+cwd)
		os.system("ssh "+ssh+" rm "+xml+name+".xml")
	except Exception, e:
		current_app.logger.error(e)
		return False
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	myDom.undefine()
	file = name+".xml"
	try:
		with open(file) as f:
			strs = f.read()
	except Exception, e:
		current_app.logger.error(e)
		return False
	xmlDom = minidom.parseString(strs)
	domainNode = xmlDom.getElementsByTagName("domain")[0]
	domainNode.getElementsByTagName("vcpu")[0].childNodes[0].nodeValue = cpuNum
	newStrs = xmlDom.toxml()
	f = open(file, "w")
	f.write(newStrs)
	f.close()
	try:
		os.system("scp "+cwd+name+".xml "+ssh+":"+xml)
		os.system("rm "+name+".xml")
	except Exception, e:
		current_app.logger.error(e)
		return False
	myDom = conn.defineXML(newStrs)
	if state:
		myDom.create()
	current_app.logger.info("modify vmachine cpu "+name+" success.")
	return True
 
def modify_memory(address, conn, name, memoryNum, xml):
	ssh = address.split("//")[1].split("/")[0]
	cwd = os.getcwd()
	cwd = cwd+'/'
	try:
		# 将远程主机的xml文件复制到当前目录下。
		os.system("scp "+ssh+":"+xml+name+".xml "+cwd)
		os.system("ssh "+ssh+" rm "+xml+name+".xml")
	except Exception, e:
		current_app.logger.error(e)
		return False
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	myDom.undefine()
	file = name+".xml"
	try:
		with open(file) as f:
			strs = f.read()
	except Exception, e:
		current_app.logger.error(e)
		return False
	xmlDom = minidom.parseString(strs)
	domainNode = xmlDom.getElementsByTagName("domain")[0]
	domainNode.getElementsByTagName("memory")[0].childNodes[0].nodeValue = memoryNum
	domainNode.getElementsByTagName("currentMemory")[0].childNodes[0].nodeValue = memoryNum
	newStrs = xmlDom.toxml()
	f = open(file, "w")
	f.write(newStrs)
	f.close()
	try:
		os.system("scp "+cwd+name+".xml "+ssh+":"+xml)
		os.system("rm "+name+".xml")
	except Exception, e:
		current_app.logger.error(e)
		return False
	myDom = conn.defineXML(newStrs)
	if state:
		myDom.create()
	current_app.logger.info("modify vmachine memory "+name+" success.")
	return True

def isexist(conn,name):
	try:
		myDom = conn.lookupByName(name)
		return True
	except:
		return False

