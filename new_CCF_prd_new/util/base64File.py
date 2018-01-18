# _*_coding:utf-8 _*_
# !/usr/bin/env python
import base64
import os

def dat2jpg(fileName):
    f0 = os.path.splitext(fileName)[0]+'.jpg'
    tag = '0'
    #print f0
    f1 = open(fileName,'r').read()
    f2 = open(f0,'wb')
    try:
       img = base64.b64decode(f1)
       f2.write(img)
       tag = '1'
    except Exception,error:
        print "异常:图片类型错误",error
    finally:
        os.remove(fileName)
    f2.close()
    return f0,tag


