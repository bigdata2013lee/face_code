#!/usr/bin/env python
# encoding: utf-8
"""
@version: python2.7
@author: ‘ex-majianqiang001‘
@license: 
@contact: 
@site: 
@software: PyCharm Community Edition
@file: ccfFaceFile.py
@time: 2017-08-18 10:25
"""
from util import file_util, base64File, face_test
import os, logging, ConfigParser, datetime, shutil, time
import multiprocessing

'''
1.将dat,jepg文件通过base64解码成.jpg文件.
2.进行人脸检测。如果检测不通过，则不移动
'''
dirlist = []
config = ConfigParser.ConfigParser()
config.readfp(open("./config.ini", "rb"))
okPath = config.get("global", "okpath")
errorPath = config.get("global", "errorpath")


def face_pic(inPathFile):
    print "========start============"
    orgJpgFile, tag = base64File.dat2jpg(inPathFile)
    orgJpgFile = orgJpgFile.split("/")[-1]
    print tag, orgJpgFile
    if tag == '0':
        print 'base64出错'
        return

    folderName = inPathFile.split("/")[-2]

    inFilePath = os.path.dirname(inPathFile)  # os.path.abspath(inPath + folderName)
    print inFilePath
    # 判断OK路径是否存在，不存在则创建
    if os.path.exists(os.path.abspath(okPath + folderName)):
        okFilePath = os.path.abspath(okPath + folderName)
    else:
        okFilePath = os.path.join(os.path.abspath("."), okPath + folderName)
        os.makedirs(okFilePath)
    # 判断error路径是否存在，不存在则创建
    if os.path.exists(os.path.abspath(errorPath + folderName)):
        errorFilePath = os.path.abspath(errorPath + folderName)
    else:
        errorFilePath = os.path.join(os.path.abspath("."), errorPath + folderName)
        os.makedirs(errorFilePath)

    if os.path.exists(os.path.join(inFilePath, orgJpgFile)):
        try:
            if (face_test.dlib_exists_face(os.path.join(inFilePath, orgJpgFile))):
                print "match face"
                shutil.move(os.path.join(inFilePath, orgJpgFile), os.path.join(okFilePath, orgJpgFile))
                # os.remove(os.path.join(inFilePath, orgJpgFile))
            else:
                shutil.move(os.path.join(inFilePath, orgJpgFile), os.path.join(errorFilePath, orgJpgFile))
        except Exception, e:
            print e


# #获取inPath路径下的所有文件放入LIST 做步长为40的处理，并且开启40个进程处理文件
def face_pic_dlib(inPath):
    func_var = file_util.getAllFiles(inPath)
    folderName = inPath.split("/")[-2]
    pool = multiprocessing.Pool(processes=40)
    for i in func_var:
        pool.apply_async(face_pic, (i,))
    pool.close()
    pool.join()
    print inPath, 'finish'
    '''
    文件处理完成后，写入图像处理日志，以便后续入库处理
    '''
    if os.path.exists(okPath + folderName):
        write_file('file_ok.txt', okPath + folderName + '/\n')
    if os.path.exists(errorPath + folderName):
        write_file('file_error.txt', errorPath + folderName + '/\n')


# 根据输入的时间生成需要处理的文件路径
def list_pic(begin, end, filename):
    d = begin
    detal = datetime.timedelta(days=1)
    ss = '/facepic/ccf_pic/inpath/' + filename + '/'
    while d <= end:
        dirlist.append(ss + d.strftime("%Y%m%d") + '/')
        d += detal


def write_file(filename, picpath):
    a = open(filename, 'a')
    a.write(picpath)
    a.close()


# if __name__ == "__main__":
#
#     #10 20161103-20170814
#     #15 20160719-20161103
#     #180 2010723-20140321; 20160112-20160719; 20140320-20160112
#     ISOT = '%Y-%m-%d %X'
#     print time.strftime(ISOT,time.localtime())
#     face_pic_dlib('/facepic/ccf_pic/testpic/15/20160720/')
#     print time.strftime(ISOT, time.localtime())
if __name__ == '__main__':
    begin = datetime.datetime(2017, 11, 7)
    end = datetime.datetime(2017, 11, 12)
    filename = '10'
    list_pic(begin, end, filename)
#    func_var = dirlist   多余的
    for i in dirlist:
        face_pic_dlib(i)
