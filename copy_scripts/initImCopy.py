#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-24 15:14
# @Author  : lvjing
# @Site    :
# @File    : ocrFileCopy.py
# @Software: PyCharm Community Edition

import datetime,os,threading,shutil,sys
from datetime import datetime, timedelta
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
    print notExist, 'notExist'
    for i in notExist:
        spath = srcim+i
        h = os.path.dirname(i)
        dpath = dstim+h
        print dpath
        if os.path.exists(dpath):
            shutil.copy2(spath, dpath)
        else:
            os.makedirs(dpath)
            shutil.copy2(spath, dpath)

#初始拷贝
def initCopy():
    begin = datetime(2017, 8, 31, 00)
    end = datetime(2017, 9, 26, 23)
    d = begin
    detal = timedelta(hours=1)
    while d <= end:
        b = d.strftime("%Y" + ll + "%m" + ll + "%d" + ll + "%H")
        srcpath1 = srcim + ll + b
        ds = d.strftime("%Y" + ll + "%m" + ll + "%d" + ll + "%H")
        dspath1 = dstim + ll + ds
        srcFile = filesList(srcpath1)
        dstFile = filesList(dspath1)
        copyFile(srcFile, dstFile)
        d += detal

if __name__ == '__main__':
    initCopy()




