# encoding: utf-8
import base64
import os
import signal

# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  #开发环境的客户端字符集
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'  # 生产环境的客户端字符集

import xmltodict
from tornado.httpclient import HTTPClient, HTTPRequest

import sys

if sys.version_info <= (2, 7):
    reload(sys)
    sys.setdefaultencoding('UTF8')

import json
import logging.config
import uuid
from datetime import datetime
from multiprocessing import Process

import yaml
from PIL import Image
from sqlalchemy import create_engine

from util_tools import create_all_log_dirs, set_log_savepath, picture_util, check_card_code

try:
    from util_tools.db_password import get_db_password
except:
    pass

wintone_card_type = '2'  # 目前只识别二代身份证正面信息

if sys.version_info >= (3, 0):
    config = yaml.load(open('./config_files/ocr_pic_wintone.yaml', 'r', encoding='utf8'))
else:
    config = yaml.load(open('./config_files/ocr_pic_wintone.yaml', 'r'))

config['pic_inpath_list'] = [os.path.abspath(x) for x in config['pic_inpath_list']]
config['pic_inpath'] = os.path.join(os.path.abspath(config['pic_inpath']))
config['pic_outpath'] = os.path.join(os.path.abspath(config['pic_outpath']), wintone_card_type)

log_config = yaml.load(open('logging.yaml', 'r'))
set_log_savepath(log_config, config['log_savepath'])
create_all_log_dirs(log_config)
logging.config.dictConfig(log_config)
log = logging.getLogger('log')

wintone_card_type_dict = {
    '1': '一代身份证',
    '2': '二代身份证正面',
    '3': '二代身份证证背面',
    '4': '临时身份证',
    '5': '驾照',
    '6': '行驶证',
    '7': '军官证',
    '8': '士兵证（暂不支持）',
    '9': '中华人民共和国往来港澳通行证',
    '10': '台湾居民往来大陆通行证',
    '11': '大陆居民往来台湾通行证',
    '12': '签证',
    '13': '护照',
    '14': '港澳居民来往内地通行证正面',
    '15': '港澳居民来往内地通行证背面',
    '16': '户口本',
    '17': '银行卡',
    '19': '车牌',
    '20': '名片',
    '1000': '居住证',
    '1001': '香港永久性居民身份证',
    '1002': '登机牌（拍照设备目前不支持登机牌的识别）',
    '1003': '边民证（A）（照片页）',
    '1004': '边民证（B）（个人信息页）',
    '1005': '澳门身份证',
    '1006': '领取凭证(AVA6支持)',
    '1007': '律师证（A）（信息页）',
    '1008': '律师证（B）（照片页）',
    '1011': '组织机构代码证',
    '1030': '全民健康保险卡',
    '1031': '台湾身份证正面',
    '1032': '台湾身份证背面',
    '1991': '文档+简体中文',
    '2991': '文档+繁体',
    '3991': '文档+纯英文',
    '1992': '长微博+简体中文',
    '2992': '长微博+繁体',
    '3992': '长微博+纯英文',
    '25': '新版台湾居民往来大陆通行证正面',
    '26': '新版台湾居民往来大陆通行证背面',
    '22': '卡式港澳通行证',
    '2008': '营业执照'
}


# 调用文通接口
def call_wintone(file_path, card_type):
    log.info('file_path={} card_type={} call_wintone start'.format(file_path, card_type))
    resp_card_info = {}
    try:
        file_bytes = open(file_path, 'rb').read()
        paramdata = '{}==##{}==##==##null'.format(base64.b64encode(file_bytes).decode(), card_type)
        requ_data = {
            'username': 'test',
            'paramdata': paramdata,
            'imgtype': os.path.splitext(file_path)[-1][1:],
            'signdata': 'NULL'
        }
        log.info('file_path={} card_type={} call_wintone SEND REQU'.format(file_path, card_type, requ_data))
        requ_body = json.dumps(requ_data)

        http_client = HTTPClient()
        http_requ = HTTPRequest(
            url=config['wintone_url'],
            method='POST',
            headers={'Content-Type': 'text/plain;charset=utf-8'},
            body=requ_body
        )
        http_resp = http_client.fetch(http_requ)
        resp_body = http_resp.body.decode(encoding='utf-8')
        log.info('file_path={} RESP'.format(file_path))

        xml_resp = resp_body.rstrip('==@@')
        xml_resp = xmltodict.parse(xml_resp)

        resp_status = int(xml_resp['data']['message']['status'])
        resp_msg = xml_resp['data']['message']['value']
        if resp_status >= 0:  # 大于等于0表示成功，小于0表示失败
            card_info_list = xml_resp['data']['cardsinfo']
            card_info = card_info_list['card']
            resp_card_info['card_type'] = card_info['@type']

            for item_info in card_info['item']:
                key = item_info['@desc']
                value = item_info.get('#text')
                resp_card_info[key] = value
        else:
            log.error('file_path={} card_type={} call_wintone ERROR: {}'.format(file_path, card_type, resp_msg))
    except:
        log.exception('file_path={} card_type={} call_wintone exception!!!'.format(file_path, card_type))

    return resp_card_info


#
def on_sub_process_exit(signo, frame):  # 子进程退出处理
    global sub_task_id
    global run_flag

    run_flag = False  # 抓取到SIGTERM时设置退出标记
    pid = os.getpid()
    log.info('[{}][{}] signo={} frame={} on_sub_process_exit'.format(sub_task_id, pid, signo, frame))


def sub_process_func(task_id, all_pic_file_list):  # 子进程处理函数
    global sub_task_id
    global run_flag

    run_flag = True
    sub_task_id = task_id
    signal.signal(signal.SIGTERM, on_sub_process_exit)

    # 每个子进程定制日志目录
    for h in log_config['handlers']:
        if 'filename' in log_config['handlers'][h]:
            p1, p2 = os.path.split(log_config['handlers'][h]['filename'])
            log_config['handlers'][h]['filename'] = os.path.join(p1, 'task_{0}'.format(sub_task_id), p2, )

    create_all_log_dirs(log_config)
    logging.config.dictConfig(log_config)
    create_all_log_dirs(log_config)

    pid = os.getpid()
    log.info('[{}][{}] sub_process_func start>>>>>>>>>>>>>>>>>>>>>>>>>'.format(sub_task_id, pid))

    db_engine = create_engine(
        config['db']['uri'].format(password=config['db'].get('password') or get_db_password(config['db']['cyberark'])),
        pool_size=2,
        echo_pool=True,
        pool_recycle=3600
    )
    for org_ph_name in all_pic_file_list[sub_task_id::config['worker_count']]:
        if not run_flag:
            break

        dest_image_list = []  # 被移动的文件
        new_image_list = []  # 新生成的文件
        pic_list = []  # 需要入库的文件
        try:
            wintone_resp_card_info = call_wintone(org_ph_name, wintone_card_type)

            # 身份证(2)的返回结果
            # {
            #     'card_type': '2',
            #     '保留': None,
            #     '姓名': '史洁',
            #     '性别': '女',
            #     '民族': '汉',
            #     '出生': '1969-07-16',
            #     '住址': '山东省郯城县庙山镇仇村二组97号',
            #     '公民身份号码': '372822196907167920',
            #     '头像': 'xxxx'
            # }
            card_code = wintone_resp_card_info.get(u'公民身份号码')
            log.info('file_path={} card_code={}'.format(org_ph_name, card_code))
            check_result, check_msg = check_card_code(card_code)
            if not check_result:
                log.info('file_path={} check_card_code fail'.format(org_ph_name))
                continue

            # 将图片移动到目的文件夹
            photo_id = 'P_{}'.format(uuid.uuid1())
            face_photo_id = 'P_{}'.format(uuid.uuid1())
            photo_id_list = [photo_id, face_photo_id]
            pic_path = org_ph_name.replace(config['pic_inpath'], config['pic_outpath'])
            pic_path = os.path.join(os.path.split(pic_path)[0], photo_id + os.path.splitext(pic_path)[-1])
            face_pic_path = os.path.join(os.path.split(pic_path)[0], face_photo_id + os.path.splitext(pic_path)[-1])
            try:
                os.makedirs(os.path.split(pic_path)[0])
            except:
                pass
            os.rename(org_ph_name, pic_path)
            # shutil.copyfile(org_ph_name, pic_path)
            dest_image_list.append((pic_path, org_ph_name, photo_id))
            pic_list.append((pic_path, photo_id, '2', org_ph_name))  # ocr原图data_source为2
            log.info('move file {} >> {}'.format(org_ph_name, pic_path))

            # 保存头像文件
            if wintone_resp_card_info.get(u'头像'):
                with open(face_pic_path, 'wb+') as f:
                    f.write(base64.b64decode(wintone_resp_card_info[u'头像'].encode()))
                new_image_list.append((face_pic_path, face_pic_path, face_photo_id))
                pic_list.append((face_pic_path, face_photo_id, '3', photo_id))  # ocr头像的data_source为3
                log.info('save face file {}'.format(face_pic_path))

            # 更新数据库
            with db_engine.begin() as db_conn:
                card_prov = int(card_code[:2])
                stat_month = datetime.today().date().replace(day=1)

                if sys.version_info >= (3, 0):
                    card_code_base64 = base64.b64encode(card_code.encode('utf8')).decode('utf8')
                else:
                    card_code_base64 = base64.b64encode(card_code)

                # 判断人员基本信息表是否存在该数据
                query_result = db_conn.execute(r'''
                    SELECT 
                        card_id,
                        person_nm,
                        addr
                    FROM facedata.fac_person_base_info  
                    WHERE card_code = :1 and card_prov = :2
                ''', (
                    card_code_base64, card_prov
                )).fetchall()

                # 更新人员基本信息表
                if query_result:
                    (card_id, person_nm, addr) = query_result[0]

                    person_nm = wintone_resp_card_info.get(u'姓名') or person_nm
                    addr = wintone_resp_card_info.get(u'住址') or addr

                    log.info('file_path={} use old card_id={} card_code={}'.format(file_path, card_id, card_code))

                    db_conn.execute(r'''
                    UPDATE facedata.fac_person_base_info 
                    SET person_nm=:1, addr=:2 
                    WHERE card_code = :3 and card_prov = :4 
                    ''', (
                        person_nm,
                        addr,
                        card_code_base64,
                        card_prov
                    ))

                else:
                    card_id = 'H_' + str(uuid.uuid1())
                    log.info('file_path={} use new card_id={} card_code={}'.format(file_path, card_id, card_code))

                    card_code = card_code
                    card_type = '1'  # 身份证默认是1
                    person_nm = wintone_resp_card_info.get(u'姓名')
                    nationality = None
                    sex = {'女': '0', '男': '1'}.get(wintone_resp_card_info.get(u'性别'))
                    nation = wintone_resp_card_info.get(u'民族')
                    try:
                        birthday = wintone_resp_card_info.get(u'出生')
                        birthday = birthday and datetime.strptime(birthday, '%Y-%m-%d')
                    except:
                        birthday = None
                    addr = wintone_resp_card_info.get(u'住址')
                    card_issued_by = None

                    db_conn.execute(r'''
                    insert into facedata.fac_person_base_info(
                      card_id,
                      card_code,
                      card_type,
                      card_prov,
                      person_nm,
                      nationality,
                      sex,
                      nation,
                      birthday,
                      addr,
                      card_issued_by
                    ) VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)
                    ''', (
                        card_id,
                        card_code_base64,
                        card_type,
                        card_prov,
                        person_nm,
                        nationality,
                        sex,
                        nation,
                        birthday,
                        addr,
                        card_issued_by
                    ))

                # 图片信息入库
                for (pic_path, photo_id, data_source, org_ph_name2) in pic_list:
                    ph_path = os.path.split(pic_path)[0]
                    ph_name = os.path.basename(pic_path)
                    space_size = os.path.getsize(pic_path) / 1024  # 单位kb

                    with Image.open(pic_path) as img:
                        pixel = '{}*{}'.format(img.size[0], img.size[1])
                        dpi = img.info.get('dpi') and '{}*{}'.format(*img.info['dpi'])
                        is_colour = picture_util.picture_is_colour(img)

                        # 图片基本信息表
                        db_conn.execute(r'''
                        insert into facedata.fac_photo_base_info(
                          stat_month,
                          photo_id,
                          ph_path,
                          ph_name,
                          space_size,
                          pixel,
                          dpi,
                          is_colour,
                          data_source,
                          org_ph_name,
                          status
                        ) VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)
                        ''', (
                            stat_month,
                            photo_id,
                            ph_path,
                            ph_name,
                            space_size,
                            pixel,
                            dpi,
                            is_colour,
                            data_source,
                            org_ph_name2,
                            '1'  # 人脸识别标识 1已识别 0未识别
                        ))

                        # 关联表
                        db_conn.execute(r'''
                        insert into facedata.fac_person_photo(
                          stat_month,
                          card_id,
                          photo_id,
                          ph_path,
                          ph_name,
                          person_nm
                        ) VALUES(:1, :2,:3,:4, :5, :6)
                        ''', (
                            stat_month,
                            card_id,
                            photo_id,
                            ph_path,
                            ph_name,
                            person_nm
                        ))

            log.info('org_ph_name={} card_code={} card_id={} photo_id_list={} process file finish'.format(org_ph_name,
                                                                                                          card_code,
                                                                                                          card_id,
                                                                                                          photo_id_list))

        except:
            log.exception('process file={} exception!!!'.format(org_ph_name))

            for (pic_path, org_ph_name, photo_id) in dest_image_list:
                try:
                    os.rename(pic_path, org_ph_name)
                    log.info('[{}] rollback move file {} >>>> {}'.format(task_id, org_ph_name, pic_path))
                except:
                    pass

            for (face_pic_path, face_pic_path, face_photo_id) in new_image_list:
                try:
                    os.remove(face_pic_path)
                    log.info('[{}] rollback delete new file {}'.format(task_id, face_pic_path))
                except:
                    pass

    log.info('[{}][{}] sub_process_func finish>>>>>>>>>>>>>>>>>>>>>>>>>'.format(task_id, pid))


def on_main_process_exit(signo=None, frame=None):
    global sub_process_list
    global main_run_flag

    main_run_flag = False

    log.info('on_main_process_exit, signo={} frame={}'.format(signo, frame))

    for (task_id, p) in sub_process_list:
        log.info('send terminate to task[{}]'.format(task_id))
        p.terminate()


def process_all_pic_file_list_step1(all_pic_file_list):
    global sub_process_list
    global main_run_flag

    sub_process_list = []
    for task_id in range(config['worker_count']):
        p = Process(target=sub_process_func, args=(task_id, all_pic_file_list,))
        p.start()
        sub_process_list.append((task_id, p))

    log.info('main process running...\nkill use >>>>>kill -SIGTERM {}'.format(os.getpid()))


def process_all_pic_file_list_step2():
    global sub_process_list
    global main_run_flag


    log.info('main process running...\nkill use >>>>>kill -SIGTERM {}'.format(os.getpid()))
    for (task_id, p) in sub_process_list:
        p.join()
    sub_process_list = []


if __name__ == '__main__':
    global sub_process_list
    global main_run_flag

    sub_process_list = []
    main_run_flag = True

    log.info('main func start >>>>>')

    if True:
        max_file_count = config['worker_count'] * 20  # 每批文件最大数据量设置为1万
        signal.signal(signal.SIGTERM, on_main_process_exit)

        all_pic_file_list = []
        for pic_inpath in config['pic_inpath_list']:
            if not main_run_flag:
                break

            for root, dirs, files in os.walk(pic_inpath):
                if not main_run_flag:
                    break

                for f in files:
                    if not main_run_flag:
                        break

                    if os.path.splitext(f)[-1] in ['.jpg']:
                        file_path = os.path.join(root, f)
                        all_pic_file_list.append(file_path)
                        log.info('add file {}'.format(file_path))
                        if len(all_pic_file_list) >= max_file_count:
                            process_all_pic_file_list_step2()
                            process_all_pic_file_list_step1(all_pic_file_list)
                            all_pic_file_list = []

        if main_run_flag and len(all_pic_file_list):
            process_all_pic_file_list_step1(all_pic_file_list)
        process_all_pic_file_list_step2()
    else:
        flag = False
        all_pic_file_list = []
        for pic_inpath in config['pic_inpath_list']:
            for root, dirs, files in os.walk(pic_inpath):
                for f in files:
                    if not main_run_flag:
                        break

                    if os.path.splitext(f)[-1] in ['.jpg']:
                        file_path = os.path.join(root, f)
                        all_pic_file_list.append(file_path)
                        flag = True
                        break
                if flag: break
            if flag: break

        all_pic_file_list = [
            'D:\Projects\ocr_pic_wintone\pic_inpath\CA7E7E93F3944D2EBEF656541AE965A7_9066c94154bfd564e0cbde6e3ac24963852_1.jpg']
        sub_process_func(0, all_pic_file_list)

    log.info('main func safe exit!!!')
