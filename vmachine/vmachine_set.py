# -*- coding: utf-8 -*-
import os
import libvirt
import sys
from xml.dom import minidom

def install_env():
	 return os.system("sudo apt-get install qemu-kvm qemu virt-manager \
		virt-viewer libvirt-bin bridge-utils")

def set_bridge():
	file = '/etc/network/interfaces'   //网络配置文件
	try:
		with open(file) as f:
			strs = f.read()
		f.close()
	except:
		return False
	if 'bridge_ports' in strs:
		print "bridge has exist!"
		return True
	else:
		nic = raw_input("请输入作为桥接的网卡名:")
		os.system("sudo /etc/init.d/networking stop")
		f = open(file,'w+')
		add_strs = "auto "+nic+"\niface "+nic+" inet manual\nauto br0\n\
iface br0 inet dhcp\nbridge_ports "+nic+"\nbridge_stp off\nbridge_fd 0"
		f.write(strs+add_strs)
		f.close()
		os.system("sudo /etc/init.d/networking start")
		print "bridge set successful!"
		return True

def define_xml():
	conn = libvirt.open('qemu:///system')
	path = os.getcwd()
	types = ['qcow2','raw','vdi','vmdk']
	for rt,dirs,files in os.walk(os.getcwd()):
		for file in files:
			if file.split('.')[1] in types:
				xml = os.path.join(rt,file.split('.')[0])+'.xml'
				filepath = os.path.join(rt,file)
				try:
					with open(xml) as f:
						strs = f.read()
				except:
					return False
				xmlDom = minidom.parseString(strs)
				domainNode = xmlDom.getElementsByTagName("devices")[0]
				domainNode.getElementsByTagName("source")[0].attributes['file'].value = filepath
				newStrs = xmlDom.toxml()
				f = open(xml, "w")
				f.write(newStrs)
				f.close()
				myDom = conn.defineXML(newStrs)
				myDom.create()
				# print domains = conn.listAllDomains()

if __name__=='__main__':
	if not install_env():
		print "环境安装失败"
		exit()
	if not set_bridge():
		print "网络配置文件路径有误，请修改路径"
		exit()
	if not define_xml():
		print "xml文件不存在"
		exit()
