#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-09-19 16:41
# @Author  : lvjing
# @Site    :
# @File    : copy_files_ip.py
# @Software: PyCharm Community Edition

from datetime import datetime,timedelta
import time
import os,sys,threading
from apscheduler.scheduler import Scheduler
path = r'/nfsc/xface_fd_id416020_vol1002_prd/'
ll = os.sep
#target = r'/nfsc/xface_fd_id416020_vol1003_prd'
'''遍历源路径下日期目录，srcpath源路径'''

def iterSubDir(srcpath):
#定义列表，用来存储结果
    lists = []
#判断路径是否存在
    if (os.path.exists(srcpath)):
    #获取该目录下的所有文件或文件夹目录
        files = os.listdir(srcpath)
        for file in files:
            #得到该文件下所有目录的路径
            m = os.path.join(srcpath,file)
            #判断该路径下是否是文件夹
            if (os.path.isdir(m)):
                #print '*********--------',m
                h = os.path.split(m)
                #print h[1]
                lists.append(h[1])
        return lists

#读取存放路径文件,截取日期目录
def read_file_path(filepath):
    file = open(filepath)
    setlist = ([])
    while 1:
        lines = file.readlines(1)
        #print type(lines)
        if not lines:
            break
        for line in lines:
            line = line.replace('\n', '')
            if ''==line:
                continue
            line = line.split(r"/")[-1]
            setlist.append(line)
        return setlist

def write_file(filename,picpath):
    a=open(filename,'a')
    a.write(picpath+"\n")
    a.close()

def copyFile():
    #遍历path下一级子目录 即日期目录
    srcPathSubDir = iterSubDir(path)
    print "111  ",srcPathSubDir
    #读取文件拷贝目录,截取日期目录
    copyFilePath = read_file_path('/wls/appsystem/cp_pic/h_model/h_model_filepath.txt')
    print copyFilePath, type(copyFilePath)
    #遍历srcPathSubDir下日期目录,copyFilePath文件中不存在的日期目录 存放到集合中
    differSet= [l for l in srcPathSubDir if l not in copyFilePath]
    target_path = ' /nfsc/xface_fd_id416020_vol1003_prd/h_model/inpath'
    #迭代差集,拼接源目录
    for dirDate in differSet:
        source_path = path + dirDate #
        os.system('cp -r ' + source_path + target_path)#拷贝差集目录至目标目录
        #拼接目标目录
        inpath = '/nfsc/xface_fd_id416020_vol1003_prd/h_model/inpath'+ll+dirDate
        #将目标路径写入 存放路径文件下
		#/opt/cp_pic/recognition/img_filepath.txt
		#/wls/appsystem/cp_pic/recognition
        write_file('/wls/appsystem/cp_pic/h_model/h_model_filepath.txt', inpath)
        print 'cp -r ' + source_path + target_path
        sys.stdout.flush()
   
#拷贝任务
def task():
    copyFile()

if __name__=='__main__':
	task()



