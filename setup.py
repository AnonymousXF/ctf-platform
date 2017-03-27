# -*- coding: utf-8 -*-
import pexpect,sys

if len(sys.argv) != 7:
      print "Usage:\n  python setup.py SMTPServer EMAILName EMAILPassword SSH_IP SSH_LoginUsername SSH_LoginPassword"
      sys.exit()
else:
      SMTPserver = sys.argv[1]
      EMAILName = sys.argv[2]
      EMAILPassword = sys.argv[3]
      SSH_IP = sys.argv[4]
      SSH_LoginUsername = sys.argv[5]
      SSH_LoginPassword = sys.argv[6]


#docker import base_environment.tar.gz
print "waiting for import image..."
try:
  result = pexpect.run('docker import base_environment.tar.gz  base_env',timeout=None)
  if "sha" not in result:
    print result
    print "Import image Error!"
    sys.exit()
  else:
    print "Import SUCCESS!"
    print "base_env ImageID: " + result + "\n"
except pexpect.EOF:
  print "Import image Error!"
  sys.exit()

#docker build
print "build platform image..."
try:
  cmd = 'docker build --build-arg SMTP=' + SMTPserver \
        + ' --build-arg EMAIL=' + EMAILName \
        + ' --build-arg PASSWORD=' + EMAILPassword \
        + ' -t platform .'
  result = pexpect.run(cmd,timeout=None)
  if "sha" not in result:
    print result
    print "Build image Error!"
    sys.exit()
  else:
    print "Build SUCCESS!\n"
except pexpect.EOF:
  print "Build Error!\nInformation:"
  print result
  sys.exit()

#docker run
print "Run image..."
try:
  containerID = pexpect.run('docker run -d -p 8001:8001 -v /home/x/Documents/docker/log:/home/log -v /home/x/Documents/docker/backup:/home/backup platform',timeout=None)
  print "platform container start SUCCESS!\n"
  print "ContainerID: " + containerID
except pexpect.EOF:
  print "Run image Error!"
  sys.exit()


#ssh
print "establish ssh connection..."
try:
  cmd = 'docker exec -it --privileged=true ' + containerID + ' bash -c "cd /root && python ssh.py"'
  result = pexpect.spawn(cmd)
  index = result.expect("请输入远程ssh连接的IP")
  if index == 0:
    print "请输入远程ssh连接的IP:"
    result.sendline(SSH_IP)
  index = result.expect("登录名")
  if index == 0:
    print "登录名："
    result.sendline(SSH_LoginUsername)
  index = result.expect("登录密码")
  if index == 0:
    print "登录密码："
    result.sendline(SSH_LoginPassword)
  result.expect("未配置ssh公私钥")
  print "未配置ssh公私钥"
  result.expect("开始配置公私钥")
  print "开始配置公私钥"
  result.expect("ssh公私钥配置成功")
  print "ssh公私钥配置成功"
  result.expect("ssh检查pass")
  print "ssh检查pass"
  result.expect("虚拟机环境检查pass")
  print "虚拟机环境检查pass"
  print "establish ssh connection SUCCESS!"
except:
  print "establish ssh connection Error!"
  sys.exit()
