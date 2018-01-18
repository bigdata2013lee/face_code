#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/12 14:27
# @Author  : ex-zhuge001
# @Site    : 
# @File    : singleInsert.py
# @Software: PyCharm

#import dbUtilTest
#import dbUtil
import cx_Oracle,uuid

#pool1 = dbUtil.getConn()
#pool1 = dbUtilTest.getConn()
#conn1 = pool1.acquire()


def getCardId(conn,cardCode,cardProv):
    #cursor1 = conn.cursor()
    getCardId = """SELECT card_id FROM facedata.fac_person_base_info WHERE card_code = :1 and card_prov = :2"""
    #cursor1.setinputsizes(100,int)
    try:
        ss = conn.execute(getCardId,(cardCode,cardProv))
        query_result= ss.fetchall()
        #cursor1.close()

        if query_result:
            card_id = query_result[0][0]
        else:
            card_id = 'H_' + str(uuid.uuid1())

        return card_id
    except cx_Oracle._Error, err:
        print 'fac_person_base_info数据查询异常', err


def insert2PerInf(conn,cardId,cardCode,cardType,cardProv):
    #print "now insert2PerInf"
    #cursor1 = conn.cursor()
    insert_PERSON_INFO = """insert into facedata.fac_person_base_info (CARD_ID,CARD_CODE,CARD_TYPE,CARD_PROV)values (:1, :2, :3, :4)"""
    #cursor1.setinputsizes(40, 100, 30, int)
    try:
        conn.execute(insert_PERSON_INFO,(cardId,cardCode,cardType,cardProv))
        #cursor1.close()
    except cx_Oracle._Error, err:
        print '插入FAC_PERSON_INFO表数据异常', err
        #conn.rollbak()
    #conn.commit()

def insert2PhoInf(conn,statMonth,photoId,phPath,phName,spaceSize,pixel,dpi,isColor,dataSource,status):
    #print "now insert2PhoInf"
    #cursor1 = conn.cursor()
    insert_PHOTO_INFO = """insert into facedata.fac_photo_base_info(STAT_MONTH,PHOTO_ID,PH_PATH,PH_NAME,SPACE_SIZE,PIXEL,DPI,IS_COLOUR,DATA_SOURCE,STATUS)values (:1, :2,:3,:4,:5,:6,:7,:8,:9,:10)"""
    #cursor1.setinputsizes(cx_Oracle.DATETIME, 40, 255, 255, 50, 50, 30, 2, 50, 2)
    try:
        conn.execute(insert_PHOTO_INFO,(statMonth,photoId,phPath,phName,spaceSize,pixel,dpi,isColor,dataSource,status))
        #cursor1.close()
    except cx_Oracle._Error, err:
        print '插入FAC_PHOTO_INFO表数据异常', err
        #conn.rollbak()
    #conn.commit()

def insert2PerPho(conn,statMonth,cardId,photoId,phPath,phName):
    #print "now insert2PerPho"
    #cursor1 = conn.cursor()
    insert_PERSON_PHOTO = """insert into facedata.fac_person_photo(STAT_MONTH,CARD_ID,PHOTO_ID,PH_PATH,PH_NAME)values (:1,:2,:3,:4,:5)"""
    #cursor1.setinputsizes(cx_Oracle.DATETIME, 40, 40, 255, 255)
    try:
        conn.execute(insert_PERSON_PHOTO,(statMonth,cardId,photoId,phPath,phName))
        #cursor1.close()
    except cx_Oracle._Error, err:
        print '插入FAC_PERSON_PHOTO表数据异常', err
        #conn.rollbak()
    #conn.commit()
