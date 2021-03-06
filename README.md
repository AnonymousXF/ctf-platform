## 安装配置说明
首先，需要安装所需的模块，具体的模块名称包含在`requirements.txt`文件中，使用以下命令可以快速安装：

```
#linux system
~/flagbase $ sudo apt-get install libvirt-bin
~/flagbase $ sudo pip install -r requirements.txt

#windows system
~/flagbase/ pip install -r requirements.txt
```

根据需求编辑 `config.py`， 文件中包括了CTF比赛的名称、注册功能的开启/关闭、比赛的开始和结束时间等配置信息。

在`config.py`中有个`cdn`变量，设置为true的时候，需要连接外网才能获取css、js等资源，否则网页样式无法正常显示。如果没有连接外网，则将其设置为false，这时会从`static`文件夹中获取相关资源。

可以编辑`database.py`中第2行来更改使用的数据库，默认使用的是SQLite。连接数据库使用的ORM框架为`peewee` ，只要`peewee`支持的数据库都能使用。

创建secrets文件，格式如下：

```
key: flasksessionkey
```

flasksession的密钥最好设置为一个随机的字符串。

**在配置SMTP服务的时候，需要配置几个环境变量：**

```
MAIL_USERNAME=xxxx@xxx.com  #邮箱的名字
MAIL_PASSWORD=xxxxx     #邮箱SMTP服务的密码
MAIL_HOST=xxxxx     #SMTP服务器
```
基本配置设置好之后，创建数据库：

```
~/flagbase $ python ctftool create-tables
Tables created.
~/flagbase $
```

通过YAML文件来导入题目，problem.yml文件示例如下：

```yml
name: Problem Name
author: ME!
category: Binary
description: binary binary binary binary. i love binary
points: 250
flag: "flag{whatever}"
```

然后使用ctftool，输入参数：

```
~/flagbase $ python ctftool add-challenge /path/to/problem.yml
Challenge added with id 1
~/flagbase $
```

 然后题目信息就会被导入数据库。

在app.py中有如下一行代码：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.debug, port=8001)
```

可以通过修改port参数来改变平台运行的端口，通过更改`config.py`文件中的debug值来开启/关闭DEBUG模式。

运行 `python app.py` ，CTF平台即可运行，注意程序运行是不需要root权限，若用sudo运行，则无法不输入与运行虚拟机的服务器建立ssh连接。 

```
~/flagbase $ python app.py
INFO:werkzeug:* Restarting with stat
WARNING:werkzeug:* Debugger is active!
INFO:werkzeug:* Debugger pin code:319-929-556
INFO:werkzeug:* Running on http://127.0.0.1:8001/(Press CTRL+C to quit)
```



## ctftool

可以使用 `ctftool`做一些操作，例如：添加题目，添加队伍，添加管理员等。 

```
#创建表
python ctftool create-tables
#删除表
python ctftool drop-tables
#添加题目
python ctftool add-challenge /path/to/problem.yml
#添加管理员
python ctftool add-admin
Username:admin
Password:password
AdminUser created.
#刷新缓存，在添加完题目后要重新刷新缓存，不然会有显示错误
python ctftool recache-solves
```

如果目录结构如下所示：

- ctf-platform
- ctf-problems
    - problem1
        - problem.yml
        - static.yml
    - problem2
        - problem.yml
        - static.yml
    - problem3
        - problem.yml
    - problem4

可以执行命令 `./ctftool scan ../ctf-problems/` 可以批量地将yaml文件中的题目信息导入数据库， 自动的生成静态文件名称，并自动那个替换yaml文件中静态文件的链接。




##虚拟机管理
管理员可以通过导航栏进入题目界面，对题目和虚拟机进行管理。
对于题目的管理，在界面中，除了题目name以外的信息都可以修改，主要是可以控制题目的开启状态，当题目处于关闭状态，则参赛人员不可回答该题。
对于虚拟机的管理，可以对虚拟机进行关闭，运行，挂起和恢复的操作，以及修改虚拟机的内存与处理器。在管理虚拟机之前，需在界面输入url，若虚拟机与平台运行在同一台服务器上，则输入qemu:///system即可，若运行在不同的服务器上，则需要在两台服务器之间配置ssh连接，并配置公钥与私钥，能够不输入密码即可远程登录进去，远程url为qemu+ssh://user@ip/system。同时还应输入虚拟机配置文件xml的路径，如FreeDOS.xml的路径为/etc/libvirt/qemu/FreeDOS.xml，则需输入/etc/libvirt/qemu/。注意所有虚拟机的xml配置文件应放在同一目录下。

## 单元测试的一些情况

通过预先设计的测试用例，判断输出的结果是否与预期相符合。

在测试的过程中，会有较长时间的等待，原因是后台程序在某几处对redis的键值对设置了有效期，在这个有效期内键值对的值不能被修改（例如在修改用户信息、提交flag等功能），如果提交会提示用户不要频繁提交，因此为了使测试用例能够通过，在其中添加了一些sleep语句进行延时，如果有必要，可以对redis键值对的有效时间进行缩短，提高单元测试的速度。

由于有对虚拟机进行单元测试，所以进行测试前，需对本机进行相关虚拟机的安装，虚拟机的环境安装：

```python
sudo apt-get install qemu-kvm
sudo apt-get install qemu
sudo apt-get install virt-manager
sudo apt-get install virt-viewer 
sudo apt-get install libvirt-bin 
sudo apt-get install bridge-utils
```

安装完成后重启系统，即可用virsh通过xml新建虚拟机，或通过virt-manager新建虚拟机均可。

单元测试的虚拟机名，设置在admin_test.py中，如：
```python
Vname = 'FreeDOS'
```

## 可能会遇到的问题

* 之前尝试在ubuntu 14.04中安装，在安装模块peewee时总是出现问题，安装成功后程序仍然显示无法识别peewee模块；在ubuntu 16.04中安装正常。
* bcrypt模块在64位windows上安装失败。
* 需要安装redis服务，在平台运行时保证redis服务处于运行状态。
* windows平台和linux平台都可以运行。
