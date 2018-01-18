#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-09-04 10:18
# @Author  : lvjing
# @Site    : 
# @File    : copy_files_ip.py
# @Software: PyCharm Community Edition

from datetime import datetime,timedelta
import time
import os,sys,threading
from apscheduler.scheduler import Scheduler

path = r'/nfsc/ccf_core_id406927_vol1004_prd/photo/'
ipaddr='10'
ll = os.sep

def write_file(filename,picpath):
    a=open(filename,'a')
    a.write(picpath+"\n")
    a.close()

def copyFile(cur):
    preDayTime = cur - timedelta(days=1)
    source_path = path + preDayTime.strftime("%Y%m%d")
    target_path = ' /facepic/ccf_pic/inpath/' + ipaddr
    print source_path + ':start_time:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    os.system('cp -r ' + source_path + target_path)

    #write copyFilePath to file
    inpath = '/facepic/ccf_pic/inpath/'+ipaddr+ll+ preDayTime.strftime("%Y%m%d")
    write_file('/wls/appsystem/cp_pic/10/copyFilePath.txt',inpath)
    print 'cp -r ' + source_path + target_path
    print source_path + ':end_time:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    sys.stdout.flush()

def task():
    syscur = datetime.now()
    copyFile(syscur)

sched = Scheduler()
sched.daemonic = False
sched.add_interval_job(task, hours=24, start_date='2017-10-17 03:00:00')
sched.start()

