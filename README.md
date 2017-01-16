## 安装说明
首先，需要安装所需的模块，具体的模块名称包含在`requirements.txt`文件中，使用以下命令可以快速安装：

```
#linux system
~/flagbase $ sudo pip install -r requirements.txt

#windows system
~/flagbase/ pip install -r requirements.txt
```

根据需求编辑 `config.py`， 文件中包括了CTF比赛的名称、注册功能的开启/关闭、比赛的开始和结束时间、邮箱SMTP服务的账号和密码等配置信息。

可以编辑`database.py`中第2行来更改使用的数据库，默认使用的是SQLite。连接数据库使用的ORM框架为`peewee` ，只要`peewee`支持的数据库都能使用。

创建secrets文件，格式如下：

```
mailgun_url: https://api.mailgun.net/v3/yourdomain.com
mailgun_key: key-yourmailgunkey
recaptcha_key: yourrecaptchakey
recaptcha_secret: yoursecret
key: flasksessionkey
```

第1、2行不用管，这里使用了邮箱的SMTP服务来代替；第3、4行是谷歌的第三方插件的公私钥，由于要翻墙才能使用，实际中取消了这一部分的功能；第5行为flasksession的密钥，最好设置为一个随机的字符串。



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
    app.run(debug=config.debug, port=8001)
```

可以通过修改port参数来改变平台运行的端口，通过更改`config.py`文件中的debug值来开启/关闭DEBUG模式。

运行 `python app.py` ，CTF平台即可运行。 

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
#刷新缓存，在添加完题目后一定要重新刷新缓存，不然会出错
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

## 可能会遇到的问题

* 之前尝试在ubuntu 14.04中安装，在安装模块peewee时总是出现问题，安装成功后程序仍然显示无法识别peewee模块；在ubuntu 16.04中安装正常。
* 需要安装redis服务，在平台运行时保证redis服务处于运行状态。
* windows平台和linux平台都可以运行。