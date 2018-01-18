#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-24 15:14
# @Author  : lvjing
# @Site    :
# @File    : ocrFileCopy.py
# @Software: PyCharm Community Edition

import datetime,os,threading,shutil
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
ll=os.sep
srcim = "/nfsc/ocr_id_id201211_vol1001_prd/im"#源
dstim = "/facepic/ocr_pic/inpath/im"#目标
"""
srcim  = "d:\\nfsc\\ocr_id_id201211_vol1001_prd\\im"
dstim = "d:\\facepic\\ocr_pic\\inpath\\im"
"""
#迭代目录下的所有文件
def go_through_folder(folder):
    for parent, folders, filenames in os.walk(folder):
        for filename in filenames:
            yield os.path.abspath(os.path.join(parent, filename))
        for folder in folders:
            go_through_folder(folder)

#遍历文件
def filesList(path):
    srcFileLists = []
    for ii in go_through_folder(path):
        srcFileLists.append(ii)
    return srcFileLists

#生成当前系统前三小时文件
def createPreHourFile(filepath,s):
    first = s - timedelta(hours=1)
    preFirstHour = first.strftime("%Y" + ll + "%m" + ll + "%d" + ll + "%H")
    preFirstHourPath = filepath + ll + preFirstHour
    L1 = filesList(preFirstHourPath)
    second = s - timedelta(hours=2)
    preSecondHour = second.strftime("%Y" + ll + "%m" + ll + "%d" + ll + "%H")
    preSecondHourPath = filepath + ll + preSecondHour
    L2 = filesList(preSecondHourPath)
    three = s - timedelta(hours=3)
    preThreeHour = three.strftime("%Y" + ll + "%m" + ll + "%d" + ll + "%H")
    preThreeHourHourPath = filepath + ll + preThreeHour
    L3 = filesList(preThreeHourHourPath)
    L1.extend(L2)
    L1.extend(L3)
    return L1

#拷贝文件
def copyFile(srcFile,dst2):
    dstFileList = []
    for j in dst2:
        j = j.split("im")[1]
        dstFileList.append(j)
    srcFileList = []
    for n in srcFile:
        n = n.split("im")[1]
        srcFileList.append(n)
    #print 'srcFileList ', srcFileList
    #print 'dstFileList ', dstFileList
    notExist = [l for l in srcFileList if l not in dstFileList]  # 不存在的集合 [年月日时分秒+文件名]
    print notExist, 'dst not existFile'
    for i in notExist:
        #f = i.split('im')[1]
        spath = srcim+i
        #print 'spath   ',spath
        #print 99999,i
        h = os.path.dirname(i)
        dpath = dstim+h
        #print dpath
        if os.path.exists(dpath):
            shutil.copy2(spath, dpath)
        else:
            os.makedirs(dpath)
            shutil.copy2(spath, dpath)

#定时拷贝
def task():
    print 111111
    s = datetime.now()
    srcFiles = createPreHourFile(srcim,s)
    dstFiles = createPreHourFile(dstim,s)
    print "srcFiles   ",srcFiles
    print "dstFiles   ",dstFiles
    copyFile(srcFiles, dstFiles)


curr = datetime.now();
#cu = curr + timedelta(hours=2)
c = curr.strftime("%Y-%m-%d %H:%M:%S")
sched = Scheduler()
sched.daemonic = False
sched.add_interval_job(task, hours=3, start_date=c)
sched.start()



