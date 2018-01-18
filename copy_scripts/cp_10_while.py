import datetime
import time
import os.path,sys

path = r'/nfsc/ccf_core_id406927_vol1003_prd/photo/'
ipaddr='10'
begin = datetime.datetime(2017,6,01)
end = datetime.datetime(2017,9,10)

d=begin
detal =datetime.timedelta(days=1)
while d<=end:
    print d.strftime("%Y%m%d")
    source_path = path + d.strftime("%Y%m%d")
    target_path =' /facepic/ccf_pic/inpath/' + ipaddr
    d += detal
    print source_path + ':start_time:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    os.system('cp -r ' + source_path + target_path)
    print 'cp -r ' + source_path + target_path
    print source_path + ':end_time:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    sys.stdout.flush()

