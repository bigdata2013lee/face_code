#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/17 15:42
# @Author  : ex-zhuge001
# @Site    : 
# @File    : changeName.py
# @Software: PyCharm Community Edition
import uuid,md5_util

def changeName(fileName):
    if (len(fileName) <= 35):
        # print "idCard is 15"
        idCard = fileName[-15:len(fileName)]
        # print idCard
        # temp_idCard = temp_name[-15:len(temp_name)]
        serviceTime = fileName[0:8] + '_' + fileName[8:14]
        return md5_util.get_md5_value(idCard) + '_' + serviceTime + '_' + str(uuid.uuid1())+ '.jpg'
    else:
        # print "idCard is 18"
        idCard = fileName[-18:len(fileName)]
        # print idCard
        # temp_idCard = temp_name[-18:len(temp_name)]
        serviceTime = fileName[0:8] + '_' + fileName[8:14]
        return md5_util.get_md5_value(idCard) + '_' + serviceTime + '_' + str(uuid.uuid1())+ '.jpg'

def getIdnum(fileName):
    if (len(fileName) <= 35):
        # print "idCard is 15"
        idCard = fileName[-15:len(fileName)]
        return idCard

    else:
        # print "idCard is 18"
        idCard = fileName[-18:len(fileName)]
        return idCard
