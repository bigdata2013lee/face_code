#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
业务描述：


'''

from util.dbutil import sqlalchemyConn
import cx_Oracle


def insert2PerDevice(conn,cardId,deviceId):

    insert_PERSON_DEVICE = """insert into facedata.FAC_PERSON_DEVICE(CARD_ID,DEVICE_ID)values (:1,:2)"""

    try:
        conn.execute(insert_PERSON_DEVICE,(cardId,deviceId))
        #cursor1.close()
    except cx_Oracle._Error, err:
        print '插入FAC_PERSON_DEVICE表数据异常', err

conn1 = sqlalchemyConn.get_conn()
def readFile():
    conn = conn1.connect()

    with open("D:/Users/zhengsiping699/Desktop/XFACE/data/face_add_deviceid_list_20171206_idno") as f:
        i = 0
        for line in f:
            i=i+1
            if i<15:
                t = line.split()
                print line
                insert2PerDevice(conn,t[0],t[1])
            else:
                break


if __name__ == "__main__":
    print '=============begin handle============'
    readFile()
    print '=============end handle=============='


