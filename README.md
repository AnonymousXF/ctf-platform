## 安装说明
根据需求编辑 `config.py`， 文件中包括了CTF比赛的名称、注册功能的开启/关闭、比赛的开始和结束时间、邮箱SMTP服务的账号和密码等配置信息。

可以编辑`database.py`中第2行来更改使用的数据库，默认使用的是SQLite。连接数据库使用的ORM框架为`peewee` ，只要`peewee`支持的数据库都能使用。

可以通过YAML文件来导入题目，示例如下：

```yml
name: Problem Name
author: ME!
category: Binary
description: binary binary binary binary. i love binary
points: 250
flag: "flag{whatever}"
```

然后使用ctftool，输入参数`./ctftool add-challenge problem.yml` ，然后题目信息就会被导入数据库。

运行 `python app.py` ，CTF平台即可运行。 可以用gunicorn或类似工具部署网站。

## ctftool

可以使用 `ctftool`做一些操作，例如：添加题目，添加队伍，添加管理员等。 如果目录结构如下所示：

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
* 需要安装redis服务。
* windows平台和linux平台都可以运行。