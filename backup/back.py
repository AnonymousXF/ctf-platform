import sqlite3
import sqlitebck
import config
import os
from datetime import *

def register_backup():
    #/home/backup/... and /home/app/... is the path in docker file system ,not the path in the host
    backup_name = "/home/backup/register_" + datetime.now().strftime('%Y%M%d_%H_%M_%S') + ".db"
    conn = sqlite3.connect("/home/app/dev.db")
    backcon = sqlite3.connect(backup_name)

    sqlitebck.copy(conn,backcon)

    conn.close()   
    backcon.close()
    print "backup complete! backup: " + backup_name

def afterRegister_backup():
    #/home/backup/... and /home/app/... is the path in docker file system ,not the path in the host
    backup_name = "/home/backup/begin_" + datetime.now().strftime('%Y%M%d_%H_%M_%S') + ".db"
    conn = sqlite3.connect("/home/app/dev.db")
    backcon = sqlite3.connect(backup_name)

    sqlitebck.copy(conn,backcon)

    conn.close()   
    backcon.close()
    print "backup complete! backup: " + backup_name

if __name__ == '__main__':
    if datetime.now() >= config.register_end:
	#/home/backup/... is the path in docker file system ,not the path in the host
        files = os.listdir("/home/backup")
	exsist = False
        for file in files:
            if "register" in file:
                exsist = True
        if not exsist:
            register_backup()
        else:
            afterRegister_backup()
    
