# encoding: utf-8
"""
@version: python2.7
@author: ‘lixiaodeng440‘
@license:
@contact:
@site:
@software: PyCharm Community Edition
@file: ccfFaceFile_pic_by_ladeng.py
@time: 2018-01-04 9:25
"""
from util import file_util, base64File, face_test
import os,  ConfigParser, datetime, shutil
import multiprocessing

#1.将dat,jepg文件通过base64解码成.jpg文件.
#2.进行人脸检测。如果检测不通过，则不移动



def face_pic(inPathFile):
    print "========start============"
    orgJpgFile, tag = base64File.dat2jpg(inPathFile)
    orgJpgFile = orgJpgFile.split("/")[-1]
    print tag, orgJpgFile
    if tag == '0':
        print 'base64出错'
        return

    folderName = inPathFile.split("/")[-2]

    inFilePath = os.path.dirname(inPathFile)  # os.path.abspath(inPath + folderName)
    print inFilePath
    # 判断OK路径是否存在，不存在则创建
    okFilePath = os.path.abspath(okPath + folderName)
    # 判断error路径是否存在，不存在则创建
    errorFilePath = os.path.abspath(errorPath + folderName)

    if os.path.exists(os.path.join(inFilePath, orgJpgFile)):
        try:
            if (face_test.dlib_exists_face(os.path.join(inFilePath, orgJpgFile))):
                print "match face"
                shutil.move(os.path.join(inFilePath, orgJpgFile), os.path.join(okFilePath, orgJpgFile))
                # os.remove(os.path.join(inFilePath, orgJpgFile))
            else:
                shutil.move(os.path.join(inFilePath, orgJpgFile), os.path.join(errorFilePath, orgJpgFile))
        except Exception, e:
            print e


# #获取inPath路径下的所有文件放入LIST 做步长为40的处理，并且开启40个进程处理文件
def face_pic_dlib(inPath):
    # 文件处理完成后，写入图像处理日志，以便后续入库处理
    if os.path.exists(okPath + folderName):
        write_file('file_ok.txt', okPath + folderName + '/\n')
    if os.path.exists(errorPath + folderName):
        write_file('file_error.txt', errorPath + folderName + '/\n')


import datetime, multiprocessing, pandas
from util import file_util


def get_days(begin, end):
    detal = datetime.timedelta(days=1)
    while True:
        if begin == end: break
        yield begin
        begin += detal


def check_dir(config, p_str, pic_ret_dir_df):
    p_path = config.get("global", "%spath" % p_str)
    p_path_df = pic_ret_dir_df.applymap(lambda pic_ret_dir: "%s%s" % (p_path, pic_ret_dir))
    p_path_df.applymap(lambda d: _f(d))

    def _f(d):
        if not os.path.exists(os.path.abspath(d)): os.makedirs(d)


if __name__ == '__main__':
    begin = datetime.datetime(2017, 11, 7)
    end = datetime.datetime(2017, 11, 12)
    days = get_days(begin, end)
    day_df = pandas.DataFrame([d for d in days])
    pic_ret_dir_df = day_df.applymap(lambda d: "10/%s" % d.strftime("%Y%m%d"))
    pic_abs_dir_df = day_df.applymap(lambda d_str: "/facepic/ccf_pic/inpath/10/%s/" % d_str)

    config = ConfigParser.ConfigParser()
    config.readfp(open("./config.ini", "rb"))
    check_dir(config, "ok", pic_ret_dir_df)
    check_dir(config, "error", pic_ret_dir_df)

    pool = multiprocessing.Pool(processes=40)

    def _f(pic_iter):
        for pic in pic_iter: pool.apply_async(face_pic, (pic,))

    pic_df = pic_abs_dir_df.applymap(lambda p: file_util.get_all_file_iter(p))
    pic_df.applymap(lambda pic_iter: _f(pic_iter))
    pool.close()
    pool.join()
