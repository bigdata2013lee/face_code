#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
业务描述：


'''

from util.dbutil import sqlalchemyConn
import xlrd
import cx_Oracle,uuid
import base64
import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')
conn1 = sqlalchemyConn.get_conn()
def readExcleFile():
    conn = conn1.connect()
    fname = "D:/Users/zhengsiping699/Desktop/XFACE/data/no_staff_data_1226.xlsx"
    bk = xlrd.open_workbook(fname)
    shxrange = range(bk.nsheets)
    try:
        sh = bk.sheet_by_name("Sheet1")
    except:
        print "no sheet in %s named Sheet1" % fname
    #获取行数
    nrows = sh.nrows
    #获取列数
    ncols = sh.ncols
    print "nrows %d, ncols %d" % (nrows,ncols)
    #获取第一行第一列数据
   # cordCode = sh.cell_value(1, 2)
   # personNm = sh.cell_value(1,3)

   # print cordCode,personNm
    row_list = []
    #获取各行数据
    # 获取各行数据
    for i in range(1, nrows):
        id_type = sh.cell_value(i,0)
        if(int(id_type) == 2):
            card_code = sh.cell_value(i, 1)
            card_prov = int(card_code[:2])
            person_nm= sh.cell_value(i, 2)[0:27]
            if sys.version_info >= (3, 0):
                card_code_base64 = base64.b64encode(card_code.encode('utf8')).decode('utf8')
            else:
                card_code_base64 = base64.b64encode(card_code)

            card_id,flag = getCardId(conn,card_code_base64,card_prov)

            if flag==False:
                insert2PerInf(conn, card_id, card_code_base64, 1, card_prov, person_nm);
            else:
                updatePerInf(conn, card_code_base64, card_prov, person_nm)
            #row_data = sh.row_values(i)
            #print row_data[2]
            #print row_data
            #row_list.append(row_data)




def insert2PerInf(conn,cardId,cardCode,cardType,cardProv,personNm):
    insert_PERSON_INFO = """insert into facedata.fac_person_base_info (CARD_ID,CARD_CODE,CARD_TYPE,CARD_PROV,PERSON_NM)values (:1,:2,:3,:4,:5)"""
    try:
        conn.execute(insert_PERSON_INFO,(cardId,cardCode,cardType,cardProv,personNm))
    except cx_Oracle._Error, err:
        print '插入FAC_PERSON_INFO表数据异常', err

def updatePerInf(conn,cardCode,cardProv,personNm):
    insert_PERSON_INFO = """UPDATE facedata.fac_person_base_info SET person_nm=:1 WHERE card_code = :2 and card_prov = :3"""
    try:
        conn.execute(insert_PERSON_INFO,(personNm,cardCode,cardProv))
    except cx_Oracle._Error, err:
        print '插入FAC_PERSON_INFO表数据异常', err

def getCardId(conn,cardCode,cardProv):

    getCardId = """SELECT card_id FROM facedata.fac_person_base_info WHERE card_code = :1 and card_prov = :2"""
    try:
        ss = conn.execute(getCardId,(cardCode,cardProv))
        query_result = ss.fetchall()

        if query_result:
            flag = True
            card_id = query_result[0][0]
        else:
            flag = False
            card_id = 'H_' + str(uuid.uuid1())

        return card_id,flag
    except cx_Oracle._Error, err:
        print 'fac_person_base_info数据查询异常', err



if __name__ == "__main__":
    print '=============begin handle============'
    begin = datetime.datetime.now()
    #readExcleFile()
    end = datetime.datetime.now()
    k = end - begin
    print k
    print '=============end handle=============='


