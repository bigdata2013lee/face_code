#_*_coding:utf-8 _*_
#!/usr/bin/env python


import os
#import socket_server
#字节转KB M G
def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes/1024
    except:
        print("fromat error")
        return "ERROR"
    return round(kb,2)

#获取文件大小
def getFileSize(file_path):
    try:
        size = os.path.getsize(file_path)
        return str(formatSize(size))
    except Exception as err:
        print(err)

#获取文件夹下指定后缀文件
def getFileDir(path,type):
    L = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == type:
                L.append(os.path.join(file))
    return L

#获取文件夹下指定后缀文件
def getMoreFileDir(path,type):
    L = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] in type:
                L.append(os.path.join(root,file))
    return L

#判断文件路径是否存在，如果不存在，则创建，此处是创建多级目录
def createFileDir(file_dir):
    if not os.path.isdir(file_dir):
           os.makedirs(file_dir)

#获取文件夹下所有文件
def getAllFiles(path):
    L = []
    for root, dirs, files in os.walk(path):
        for file in files:
            L.append(os.path.join(root,file))
    return L

'''
ss = getMoreFileDir('D:\\Users\\ex-zhuge001\\Desktop\\pic1','.dat')
aa = 'D:\\Users\\ex-zhuge001\\Desktop\\pic1\\20160319\\2016011200000121758530103197112231517.dat'
if '_' in aa:
    print 1
    print aa
else:
    print 0
    print aa
'''
