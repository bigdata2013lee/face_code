#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/17 17:03
# @Author  : ex-zhuge001
# @Site    : 
# @File    : sqlalchemyConn.py
# @Software: PyCharm

from sqlalchemy import create_engine
import cyberark,aseDecode

#password, key = cyberark.get_password()  # 获取密码
#pwd = aseDecode.aseDecode(password, key)  # 解密
user = 'faceopr'
password = 'test12345'

dev='oracle+cx_oracle://faceopr:%s@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=10.20.130.241)(PORT=1543))(ADDRESS=(PROTOCOL=TCP)(HOST=10.20.130.242)(PORT=1543)))(CONNECT_DATA=(SERVICE_NAME=srv_d0face_face_1)))'%password

def get_conn():
    db_engine = create_engine(dev, pool_size=2, echo_pool=True, pool_recycle=3600)
    print "connect 2 DB conn"
    #return db_engine.connect()
    return db_engine





