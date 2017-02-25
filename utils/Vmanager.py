import libvirt
import sys
from xml.dom import minidom

def createConnection(address):
	try:
		conn = libvirt.open(address)
		return conn
	except:
		return False

def closeConnection(conn):
	try:
		conn.close()
		return True
	except:
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
		return 1
	except:
		return 0

def suspendDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.suspend()
		return 1
	except:
		return 0

def resumeDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.resume()
		return 1
	except:
		return 0

def destroyDom(conn, name):
	myDom = conn.lookupByName(name)
	try:
		res = myDom.destroy()
		return 1
	except:
		return 0

def modify_cpu(conn, name, cpuNum):
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	xml = "/etc/libvirt/qemu/"+name+".xml"
	with open(xml) as f:
		strs = f.read()
	xmlDom = minidom.parseString(strs)
	domainNode = xmlDom.getElementsByTagName("domain")[0]
	domainNode.getElementsByTagName("vcpu")[0].childNodes[0].nodeValue = cpuNum
	newStrs = xmlDom.toxml()
	f = open(xml, "w")
	f.write(newStrs)
	myDom = conn.defineXML(newStrs)
	if state:
		myDom.create()
 
def modify_memory(conn, name, memoryNum):
	myDom = conn.lookupByName(name)
	state = myDom.isActive()
	if state:
		destroyDom(conn, name)
	xml = "/etc/libvirt/qemu/"+name+".xml"
	with open(xml) as f:
		strs = f.read()
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

def isexist(conn,name):
	try:
		myDom = conn.lookupByName(name)
		return True
	except:
		return False

