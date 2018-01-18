#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/12 13:59
# @Author  : ex-zhuge001
# @Site    : 
# @File    : singleHandleCCF.py
# @Software: PyCharm

'''
业务描述：
1.遍历OK和非OK的两个文件夹下所有.jpg文件
2.信息入库，OK 1 非KO 0 PS：先查询人员信息表获取card_id,如果没有就自己生成
3.更名（身份证MD+业务时间+UUID）
'''

import time,os,base64,uuid,logging,datetime
from util import file_util,picture_util ,changeName,id_card
from util.dbutil import singleInsertsqlacl
import multiprocessing
from util.dbutil import sqlalchemyConn




#/wls/applogs/new_CCF_prd/singleCCF.log
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y, %b, %d, %H:%M:%S', filename='/wls/applogs/new_CCF_prd/singleCCF.log', filemode='a')

conn1 = sqlalchemyConn.get_conn()
#conn = pool1.acquire()
ll = os.sep

# 文件处理主程序
def HandleData(filename):
    #print filename

    if '-' not in filename.split(ll)[-1]:
        #print 'handle files',filename
        # 图片路径信息orgJpgFile == /opt/111/2016/12345.jpg
        orgJpgFile = filename

        # 图片文件名返回样例 12345.jpg
        orgfileName = orgJpgFile.split(ll)[-1]
        orgfileName = orgfileName.split('.')[0]
        # 返回样例 /opt/111/2016
        fullfolderName = os.path.dirname(orgJpgFile)+ll
        # 返回样例 /2016/
        # folderName = orgJpgFile.split(ll)[-2]
        # 图片内容信息
        fileCapactiy = file_util.getFileSize(orgJpgFile)
        fileSize = picture_util.getPictureSize(orgJpgFile)
        fileDpi = picture_util.getPictureDpi(orgJpgFile)
        isColor = '5'
        # isColor = picture_util.pictureIsColor(orgJpgFile)
        # if isColor == 3:
        #    break
        # 插入数据库所需信息
        serviceTime = orgfileName[:8]
        idnum = changeName.getIdnum(orgfileName)
        cardCode = base64.b64encode(idnum)
        photoID = 'P_' + str(uuid.uuid1())
        #cardID = 'H_' + str(uuid.uuid1())
        mouth = serviceTime[:6]
        mouth = datetime.datetime.strptime(mouth, "%Y%m").date()
        #print orgfileName
        #print idnum
        card_prov = int(idnum[0:2])
        dbName = changeName.changeName(orgfileName)

        conn = conn1.connect()

        #cardID = singleInsertsqlacl.getCardId(conn,cardCode, card_prov)
        #print cardID
        checkidnum = id_card.checkIdcard(idnum.upper())
        if checkidnum[0]==1:
            #print 'OK file insert2DB'
            with conn.begin() as db_trans:
                cardID = singleInsertsqlacl.getCardId(conn,cardCode, card_prov)
                try:
                    singleInsertsqlacl.insert2PerInf(conn, cardID, cardCode, '1', card_prov)
                except Exception as e:
                    logging.info(e)
                    # print e

                #print orgJpgFile
                if 'okpath' in orgJpgFile:
                    #print ">>>>>>>>>>>>"
                    singleInsertsqlacl.insert2PhoInf(conn, mouth, photoID, fullfolderName, dbName, fileCapactiy, fileSize, fileDpi,isColor, '1', '1')
                else:
                #print ">>>>>>>>>>>>"
                    singleInsertsqlacl.insert2PhoInf(conn, mouth, photoID, fullfolderName, dbName, fileCapactiy, fileSize,fileDpi, isColor, '1', '0')
                singleInsertsqlacl.insert2PerPho(conn, mouth, cardID, photoID, fullfolderName, dbName)

                #conn.commit()

                #print 'files rename'
                # 原文件更名

                os.rename(os.path.join(fullfolderName, orgJpgFile), os.path.join(fullfolderName, dbName))

        else:
            logging.info("idCard is ERR:" + str(idnum)+':'+checkidnum[1])






#将处理完毕的目录写入文件
def write_file(filename,picpath):

    a=open(filename,'a')
    a.write(picpath + '\n')
    a.close()

#获取inPath路径下的所有jpg文件放入LIST 做步长为40的处理，并且开启40个进程处理文件
def OKhandleMul(inPath):
    logging.info(inPath)
    #print inPath
    if 'okpath' in inPath:
        logging.info('OK inpath ' + inPath)
    else:
        logging.info('ERR inpath ' + inPath)

    func_var = file_util.getMoreFileDir(inPath,'.jpg')
    #print func_var
    #/facepic/ccf_pic/output/okpath/20160905/ ==> 20160905
    #folderName = inPath.split(ll)[-2]
    pool = multiprocessing.Pool(processes=40)
    for i in func_var:
        pool.apply_async(HandleData,(i,))
    pool.close()
    pool.join()
    logging.info(inPath + 'finish')
    #print inPath,'finish'
    '''
    文件处理完成后，写入处理日志，以便后续检查
    '''
    if 'okpath' in inPath:
        if os.path.exists(inPath):
            write_file('./OKhandler.txt',inPath)
    else:
        if os.path.exists(inPath):
            write_file('./ERRhandler.txt',inPath)


if __name__ == "__main__":

    if os.path.exists('./ERRhandler.txt'):
        files = './ERRhandler.txt'
    else:
        files = open('./ERRhandler.txt', 'w')
        files.close()

    if os.path.exists('./OKhandler.txt'):
        files = './OKhandler.txt'
    else:
        files = open('./OKhandler.txt', 'w')
        files.close()

    OKLIST = []
    ERRORLIST = []

    logging.info('=============begin handle============')
    #print '=============begin handle============'

    while 1:
        with open('./file_ok.txt', 'r') as file_ok:
            fileOK = [line.strip() for line in file_ok.readlines()]
        with open('./file_error.txt', 'r') as file_error:
            fileERR = [line.strip() for line in file_error.readlines()]
        with open('./OKhandler.txt', 'r') as OKhandler:
            handleOK = [line.strip() for line in OKhandler.readlines()]
        with open('./ERRhandler.txt', 'r') as ERRhandler:
            handleERR = [line.strip() for line in ERRhandler.readlines()]
        OKLIST = list(set(fileOK) - set(handleOK))
        ERRORLIST = list(set(fileERR) - set(handleERR))

        HANDLELIST = OKLIST+ERRORLIST
        #print 'HANDLELIST : ', HANDLELIST
        print HANDLELIST

        # 使用多进程执行
        for i in sorted(HANDLELIST):
            OKhandleMul(i)

        print '===============handle over sleep 600s==============='
        logging.info('===============handle over sleep 600s===============')
        time.sleep(600)
