import libvirt
import sys
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

# def getConnInfo(conn):
# 	print "***********Host info ************"
# 	print "Hostname: "+conn.getHostname()
# 	print "FreeMemory: "+str(conn.getFreeMemory())
# 	print "Type: "+conn.getType()
# 	print "URI: "+conn.getURI()+'\n'

def getDomInfoByName(conn, name):
	myDom = conn.lookupByName(name)
	return str(myDom.maxMemory()/1024),str(myDom.info()[3]),str(myDom.state(0)[0])

def startDom(conn, name, xml):
	xml = xml+"/"+name+".xml"
	with open(xml) as f:
		strs = f.read()
	xmlDom = minidom.parseString(strs)
	newStrs = xmlDom.toxml()
	myDom = conn.defineXML(newStrs)
	try:
		res = myDom.create()
		current_app.logger.info("create vmachine "+name+" success.")
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

def modify_cpu(conn, name, cpuNum, xml):
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	xml = xml+name+".xml"
	try:
		with open(xml) as f:
			strs = f.read()
	except Exception, e:
		current_app.logger.error(e)
		return False
	xmlDom = minidom.parseString(strs)
	domainNode = xmlDom.getElementsByTagName("domain")[0]
	domainNode.getElementsByTagName("vcpu")[0].childNodes[0].nodeValue = cpuNum
	newStrs = xmlDom.toxml()
	f = open(xml, "w")
	f.write(newStrs)
	myDom = conn.defineXML(newStrs)
	if state:
		myDom.create()
	current_app.logger.info("modify vmachine cpu "+name+" success.")
	return True
 
def modify_memory(conn, name, memoryNum, xml):
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	xml = xml+name+".xml"
	try:
		with open(xml) as f:
			strs = f.read()
	except Exception, e:
		current_app.logger.error(e)
		return False
	xmlDom = minidom.parseString(strs)
	domainNode = xmlDom.getElementsByTagName("domain")[0]
	domainNode.getElementsByTagName("memory")[0].childNodes[0].nodeValue = memoryNum
	domainNode.getElementsByTagName("currentMemory")[0].childNodes[0].nodeValue = memoryNum
	newStrs = xmlDom.toxml()
	f = open(xml, "w")
	f.write(newStrs)
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

