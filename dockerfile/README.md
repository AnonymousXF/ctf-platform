### Dockerfile使用说明

1、首先需要有基础环境的镜像文件：base_environment.tar.gz

​	获取镜像的地址： [暂无]()

2、将镜像文件导入Docker，生成本地镜像：

```shell
#进入存放镜像文件的目录
cat base_environment.tar.gz | docker import - base_env
```

完成后，查看本地镜像是否导入成功：

```shell
#导入成功后即能看到镜像
docker images

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
base_env            latest              bac954d42338        47 seconds ago      1.27 GB
```

3、crontab配置文件

```shell
#文件形式如下：
# m   h   dom   mon   dow   command
# 分  时   日   月   星期   命令
*/30 * * * * python /home/app/backup/back.py
#意义为每隔半小时执行一次指定脚本，脚本路径为docker中的路径，
#更为具体的crontab配置文件说明参考网上教程
```

这里，root文件为crontab的配置文件，在dockerfile部署镜像时会将其添加到docker中的指定目录下，并启动crontab服务 。

4、dockerfile部署

在docker build之前，提前将一些配置文件修改好（源码文件夹中的gun.py，config.py，backup/config.py）

使用docker build，docker run生成平台镜像并运行：

```shell
#进入dockerfile所在的目录
docker build --build-arg SMTP=your.smtp.server --build-arg EMAIL=your email --build-arg PASSWORD=your password -t IMAGE_NAME .(最后这个 . 一定不要漏掉)
#build完成后
docker run -d -p 8001:8001 -v /home/x/Documents/log:/home/log -v /home/x/Documents/backup:/home/backup IMAGE_NAME
# -v为挂载目录，作为共享目录， -p进行端口映射，平台运行在容器8001端口，选择合适可用的宿主端口来映射
# -d设置为后台运行
```

参照以上命令中的挂载目录，列出了dockerfile所在目录的结构以及运行容器中的目录结构：

部署的文件结构如下：

|--Dockerfile Folder

​	|--backup （共享目录，挂载docker容器中的backup目录，文件夹名字任取，docker run的时候 -v 后写上对应的文件夹路径）

​	|--log （共享目录，挂载docker容器中的log目录，文件夹名字任取，docker run的时候 -v 后写上对应的文件夹路径）

​	|--Dockerfile （dockefile文件）

​	|--ctf_platform （源码文件夹）

​	|--root （crontab配置文件）

部署后，运行的容器中的文件结构如下：

|--home

​	|--backup（用于放置备份的数据库的目录）

 	|--log （用于放置gunicorn启动后access.log和error.log的目录）

​	|--app （平台源码目录）





部署完成后，即可通过映射到宿主机器的端口访问。



5、docker中运行一些命令

生成SSH公私钥：

```
docker exec -it ContainerID ssh-keygen -t rsa

#生成后，将公钥拷贝到宿主机器，复制到配置虚拟机的服务器中
docker cp ContainerID:/path/to/public_key /destination/to/host
```

创建管理员账户：

```
docker exec -it ContainerID python ctftool add-admin
```

导入题目信息：

```
docker exec -it ContainerID python ctftool add-challenge /path/to/problem.yml/in/docker
docker exec -it ContainerID python ctftool recache-solves
```

在docker中运行测试：

```
docker exec -it ContainerID bash -c "cd test && python allTest.py"
```



