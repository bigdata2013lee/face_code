# -*- coding: utf-8 -*-
import hashlib
import json
import urllib2

import time
from datetime import datetime

try:
    from util_tools import aseDecode
except:
    pass

def get_db_password(config):
    requ_data = {
        'requestId': str(int(time.time()*1000)),
        'requestTime': datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3],
        'appId': config['appId'],
        'safe': config['safe'],
        'folder': config['folder'],
        'object': config['object'],
        'key': config['key'],
        'sign': hashlib.sha256(config['sign']).hexdigest(),
    }
    requ_data = json.dumps(requ_data)
    requ_body = requ_data.encode('utf-8')

    requ_headers = {'Content-Type': 'application/json'}

    http_requ = urllib2.Request(url=config['url'], headers=requ_headers, data=requ_body)
    http_resp = urllib2.urlopen(http_requ)
    resp_body = http_resp.read().decode('utf-8')

    resp_data = json.loads(resp_body)

    password = resp_data['password']

    pwd = aseDecode.aseDecode(password, config['key'])
    return pwd
