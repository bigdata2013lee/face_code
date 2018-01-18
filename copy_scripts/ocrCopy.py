#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-10-17 10:57
# @Author  : lvjing
# @Site    : 
# @File    : ocrCopy.py
# @Software: PyCharm Community Edition
import datetime,os,threading,shutil,sys
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
import time

ll=os.sep
srcocr = "/nfsc/ocr_id_id201211_vol1001_prd/ocr/"#源
dstocr = "/facepic/ocr_pic/inpath/ocr"#目标

def copyFile(cur):
    preDayTime = cur - timedelta(days=1)
    source_path = srcocr + preDayTime.strftime("%Y" + ll + "%m" + ll + "%d")
    target_path = '/facepic/ocr_pic/inpath/ocr'+ll+preDayTime.strftime("%Y" + ll + "%m")
    print source_path , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if os.path.exists(source_path):
        if not os.path.exists(target_path):
            os.system('mkdir -p '+ target_path)
        os.system('cp -r ' + source_path + " "+target_path)
    else:
        print source_path +'不存在',time.strftime("%Y" + ll + "%m" + ll + "%d", time.localtime(time.time()))
    sys.stdout.flush()

def task():
    syscur = datetime.now()
    copyFile(syscur)

#task()
sched = Scheduler()
sched.daemonic = False
sched.add_interval_job(task, hours=24, start_date='2017-10-25 03:00:00')
sched.start()
"""
preDayTime = datetime.now() - timedelta(days=1)
print preDayTime
source_path = srcocr + preDayTime.strftime("%Y" + ll + "%m" + ll + "%d")
print source_path
"""
