#!/usr/bin/env python
#coding=utf-8

import json
import urllib2
import hashlib

def get_password():
    #测试
    url = "https://test-ccp.paic.com.cn/pidms/rest/pwd/getPassword"
    #sign
    sha11 = hashlib.sha256('App_XFACE_CORE__ae35c0&ef8ac7645a991ecc').hexdigest()
    #
    busiData = {"requestId":""
               ,"requestTime":"20170726195910111",
                "requestId":"",
                "appId":"App_XFACE_CORE__ae35c0",
                "safe":"AIM_XFACE_CORE",
                "folder":"root",
                "object":"faceopr",
                "key":"ef8ac7645a991ecc",
                "sign":sha11}


    req_dict = dict(busiData.items())
    req_json = json.dumps(req_dict)
    req_post = req_json.encode('utf-8')
    #print(req_post)

    headers = {'Content-Type': 'application/json'}
    req = urllib2.Request(url=url, headers=headers, data=req_post)
    res = urllib2.urlopen(req)
    res = res.read().decode('utf-8')
    #return res
    password = json.loads(res)['password']
    key = json.loads(req_post)['key']
    return password,key
