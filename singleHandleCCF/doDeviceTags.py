#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
业务描述：


'''

from util.dbutil import sqlalchemyConn
import cx_Oracle


def insert2DeviceTag(conn,deviceId,tagvalue):

    insert_DEVICE_TAG = """insert into facedata.fac_device_tag(DEVICE_ID,TAG_VALUE)values (:1,:2)"""

    try:
        conn.execute(insert_DEVICE_TAG,(deviceId,tagvalue))
        #cursor1.close()
    except cx_Oracle._Error, err:
        print '插入fac_device_tag表数据异常', err

conn1 = sqlalchemyConn.get_conn()
def readFile():
    conn = conn1.connect()

    with open("D:/Users/zhengsiping699/Desktop/XFACE/data/tdid_tags.log") as f:
        i = 0
        for line in f:
 #           i=i+1
 #          if i<15:
            t = line.strip().split("|")
            tags = t[1].split(",")[1:]
            #print t[0],tags
            if t[0]:
                for tag in tags:
                    if tag:
                        insert2DeviceTag(conn,t[0],tag)
 #           else:
 #              break


if __name__ == "__main__":
    print '=============begin handle============'
    readFile()
    print '=============end handle=============='


