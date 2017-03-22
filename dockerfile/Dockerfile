FROM base_env

#parameters
ARG SMTP
ARG EMAIL
ARG PASSWORD

#environments variables
ENV MAIL_HOST $SMTP
ENV MAIL_USERNAME $EMAIL
ENV MAIL_PASSWORD $PASSWORD

#change time
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
&&  echo "Asia/Shanghai" > /etc/timezone


#mkdir
RUN mkdir /home/backup
RUN mkdir /home/log
RUN mkdir /home/app

#add root(or other user) crontab
ADD root /var/spool/cron/crontabs/root
RUN chown -R root:crontab /var/spool/cron/crontabs/root \
&&  chmod 600 /var/spool/cron/crontabs/root


#add source code
ADD ctf_platform /home/app
ADD ctf_platform/ssh.py /root/ssh.py

#VOLUME
VOLUME /home/backup

WORKDIR /home/app

#create tables
RUN python ctftool create-tables

#expose port
EXPOSE 8001

RUN chmod 777 /home/app/startup.sh

#start redis,cron
CMD ["./startup.sh"]
