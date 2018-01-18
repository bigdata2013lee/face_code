# encoding: utf-8
import base64
import os

# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  #开发环境的客户端字符集
import signal

os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8' #生产环境的客户端字符集

import sys
if sys.version_info <= (2, 7):
    reload(sys)
    sys.setdefaultencoding('UTF8')

import json
import logging.config
import uuid
from datetime import datetime
from multiprocessing import Process
import time

import yaml
from PIL import Image
from sqlalchemy import create_engine

from util_tools import create_all_log_dirs, set_log_savepath, picture_util, check_card_code

try:
    from util_tools.db_password import get_db_password
except:
    pass

config = yaml.load(open('./config_files/h_model.yaml', 'r'))
config['pic_inpath'] = os.path.abspath(config['pic_inpath'])
config['pic_outpath'] = os.path.abspath(config['pic_outpath'])

log_config = yaml.load(open('logging.yaml', 'r'))
set_log_savepath(log_config, config['log_savepath'])
create_all_log_dirs(log_config)
logging.config.dictConfig(log_config)
log = logging.getLogger('log')

def on_sub_process_exit(signo, frame): #子进程退出处理
    global sub_task_id
    global run_flag

    run_flag = False   #抓取到SIGTERM时设置退出标记
    pid = os.getpid()
    log.info('[{}][{}] signo={} frame={} on_sub_process_exit'.format(sub_task_id, pid, signo, frame))

def sub_process_func(task_id, all_log_file_path_list): #子进程处理函数
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

    pid=os.getpid()
    log.info('[{}][{}] sub_process_func start>>>>>>>>>>>>>>>>>>>>>>>>>'.format(sub_task_id, pid))

    db_engine = create_engine(
        config['db']['uri'].format(password=config['db'].get('password') or get_db_password(config['db']['cyberark'])),
        pool_size=2,
        echo_pool=True,
        pool_recycle=3600
    )

    for log_file_path in all_log_file_path_list[sub_task_id::config['worker_count']]:
        if not run_flag:
            log.info('[{}][{}] run_flag=False break'.format(sub_task_id, pid))
            break

        log.info('[{}][{}] process file {} start@@@@@@@@@@@'.format(sub_task_id, pid, log_file_path))

        # time.sleep(5)
        # continue

        try:
            file_success_flag = True
            success_count = 0
            with open(log_file_path) as f_log:
                # stat_month 从日志名中提取或者使用当月时间
                try:
                    # oa.log.2016-11-18
                    stat_month = datetime.strptime(os.path.basename(log_file_path).split('.')[-1], '%Y-%m-%d').date().replace(day=1)
                except:
                    stat_month = datetime.today().date().replace(day=1)

                parent_path = os.path.abspath(os.path.join(os.path.split(log_file_path)[0], '../'))
                while True:
                    if not run_flag:
                        log.info('[{}][{}] run_flag=False break'.format(sub_task_id, pid))
                        file_success_flag = False
                        break

                    l = f_log.readline()
                    if not l:
                        break

                    if 'bound_id' not in l:
                        continue

                    json_str = None
                    card_code = None
                    dest_image_list = []
                    try:
                        json_str = l.split('[INFO]')
                        if len(json_str) != 2:
                            # 只处理包含INFO的日志放弃ERROR日志
                            continue

                        json_str = json_str[-1]

                        json_data = json.loads(json_str)

                        link_id = 'L_' + str(uuid.uuid1())

                        card_code = json_data['user_id']
                        bound_id = json_data['bound_id']
                        if bound_id.startswith('6222'): #排除测试数据
                            log.info('[{}][{}] skip bound_id {}'.format(sub_task_id, pid, bound_id))
                            continue
                        app_id = json_data.get('ext_info',{}).get('request_obj', {}).get('app_id')
                        person_id = json_data.get('ext_info',{}).get('request_obj', {}).get('person_id') or json_data.get('ext_info',{}).get('request_obj', {}).get('userId')
                        time_end = json_data['time_end']
                        time_start = json_data['time_start']

                        # 检测号码的合法性
                        card_code_result, card_code_msg = check_card_code(card_code)
                        log.info('[{}][{}] card_code={} card_code_result={} start>>>>'.format(sub_task_id, pid, card_code, card_code_result))

                        # 获取待处理图片的地址
                        try:
                            origin_image_list = json_data['local_features'].values()
                        except:
                            origin_image_list = json_data['local_images'].values()

                        # /wls/applogs/OAServer/20170614/person1043982867_065432_923583_6a165f02-6bf5-4658-a970-0ff2eb11d5f4.jpg
                        origin_image_list = [os.path.join(parent_path, 'image', p.strip().split('/')[-1]) for p in origin_image_list]
                        if not origin_image_list:
                            continue

                        # 将图片移动到目的文件夹
                        for org_ph_name in origin_image_list:
                            # 判断文件是否存在
                            if not os.path.exists(org_ph_name):
                                log.warning('[{}][{}] card_code={} file={} not exists!!!!!'.format(sub_task_id, pid, card_code, org_ph_name))
                                continue

                            # 判断是否是图片文件
                            try:
                                with Image.open(org_ph_name) as f_img:
                                    f_img.verify()
                            except:
                                log.info('[{}][{}] log_file={} image_file={} file broken!!! \n{}'.format(sub_task_id, pid, log_file_path, org_ph_name, json_str))
                                continue

                            photo_id = 'P_{}'.format(uuid.uuid1())
                            pic_path = org_ph_name.replace(config['pic_inpath'], config['pic_outpath'])
                            pic_path = os.path.join(os.path.split(pic_path)[0], photo_id + os.path.splitext(pic_path)[-1])
                            try:
                                os.makedirs(os.path.split(pic_path)[0])
                            except:
                                pass
                            os.rename(org_ph_name, pic_path)
                            dest_image_list.append( (pic_path, org_ph_name, photo_id) )
                            log.info('[{}] move file {} {} >>>> {}'.format(sub_task_id, photo_id, org_ph_name, pic_path))

                        if not dest_image_list:
                            continue

                        # 对每一张图片进行入库操作
                        card_id = None

                        if sys.version_info >= (3, 0):
                            card_code_base64 = base64.b64encode(card_code.encode('utf8')).decode('utf8')
                        else:
                            card_code_base64 = base64.b64encode(card_code)

                        db_conn = db_engine.connect()
                        with db_conn.begin() as db_trans:

                            if card_code_result:
                                card_prov = int(card_code[:2])
                                query_result = db_conn.execute(r'''
                                    SELECT 
                                        card_id
                                    FROM facedata.fac_person_base_info  
                                    WHERE card_code = :1 and card_prov = :2
                                ''', (
                                    card_code_base64, card_prov
                                )).fetchall()

                                if query_result:
                                    card_id = query_result[0][0]
                                else:
                                    card_id = 'H_' + str(uuid.uuid1())
                                    card_type = '1'  #身份证默认是1

                                    # 插入FAC_PERSON_BASE_INFO
                                    db_conn.execute(r'''
                                    insert into facedata.fac_person_base_info(
                                      card_id,
                                      card_code,
                                      card_prov,
                                      card_type
                                    ) VALUES(:1, :2,:3, :4)
                                    ''', (
                                        card_id,
                                        card_code_base64,
                                        card_prov,
                                        card_type
                                    ))

                            for (pic_path, org_ph_name, photo_id) in dest_image_list:
                                ph_path = os.path.split(pic_path)[0]
                                ph_name = os.path.basename(pic_path)
                                space_size = os.path.getsize(pic_path) / 1024  # 单位kb

                                with Image.open(pic_path) as img:
                                    pixel = '{}*{}'.format(img.size[0], img.size[1])
                                    dpi = img.info.get('dpi') and '{}*{}'.format(*img.info['dpi'])
                                    is_colour = picture_util.picture_is_colour(img)
                                    data_source = '5'  # H模型是5

                                    if card_id:
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
                                          org_ph_name
                                        ) VALUES(:1, :2,:3,:4,:5,:6,:7,:8, :9, :10)
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
                                            org_ph_name
                                        ))

                                        # 关联表
                                        db_conn.execute(r'''
                                        insert into facedata.fac_person_photo(
                                          stat_month,
                                          card_id,
                                          photo_id,
                                          ph_path,
                                          ph_name
                                        ) VALUES(:1, :2,:3,:4, :5)
                                        ''', (
                                            stat_month,
                                            card_id,
                                            photo_id,
                                            ph_path,
                                            ph_name
                                        ))

                                    # E模型数据表
                                    db_conn.execute(r'''
                                    insert into facedata.fac_photo_base_info_model( 
                                      stat_month,
                                      photo_id,
                                      ph_path,
                                      ph_name,
                                      space_size,
                                      pixel,
                                      dpi,
                                      is_colour,
                                      data_source,
                                      bound_id,
                                      app_id,
                                      person_id,
                                      link_id,
                                      time_start,
                                      time_end,
                                      user_id,
                                      status
                                    ) VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17)
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
                                        bound_id,
                                        app_id,
                                        person_id,
                                        link_id,
                                        time_start,
                                        time_end,
                                        card_code_base64,
                                        ['0', '1'][card_id != None]  # 有身份证的存1
                                    ))

                        success_count += 1
                        log.info('[{}][{}] card_code={} finish<<<<'.format(sub_task_id, pid, card_code))
                    except:
                        file_success_flag = False
                        log.exception('[{}][{}] card_code={} process file {} json data exception!!!\n{}'.format(sub_task_id, pid, card_code, log_file_path, json_str))

                        for (pic_path, org_ph_name, photo_id) in dest_image_list:
                            try:
                                os.rename(pic_path, org_ph_name)
                                log.info('[{}] rollback move file {} >>>> {}'.format(sub_task_id, org_ph_name, pic_path))
                            except:
                                pass

            log.info('[{}][{}] process file {} file_success_flag={} success_count={} finish@@@@@@@@@@'.format(sub_task_id, pid, log_file_path, file_success_flag, success_count))

            # 移动日志文件
            if file_success_flag:
                new_log_file_path = log_file_path.replace(config['pic_inpath'], config['pic_outpath'])
                try:
                    os.makedirs(os.path.split(new_log_file_path)[0])
                except:
                    pass
                os.rename(log_file_path, new_log_file_path)
                log.info('[{}] move log file {} >>>> {}'.format(sub_task_id, log_file_path, new_log_file_path))

        except:
            log.exception('[{}][{}] process file {} exception!!!'.format(sub_task_id, pid, log_file_path))

    log.info('[{}][{}] sub_process_func finish>>>>>>>>>>>>>>>>>>>>>>>>>'.format(sub_task_id, pid))


def on_main_process_exit(signo=None, frame=None):
    global sub_process_list

    log.info('on_main_process_exit, signo={} frame={}'.format(signo, frame))

    for (task_id, p) in sub_process_list:
        log.info('send terminate to task[{}]'.format(task_id))
        p.terminate()

# 将日志文件移回到原文件夹下面
if __name__ == '__main__2':
    def go_log_image_folder(folder):
        if not os.path.isdir(folder):
            return

        path_list = os.listdir(folder)
        if set(path_list) == set(['image', 'log']):
            if os.path.isdir(os.path.join(folder, 'image')) and os.path.isdir(os.path.join(folder, 'log')):
                yield folder
                return

        for p in path_list:
            p = os.path.join(folder, p)
            if os.path.isdir(p):
                for p2 in go_log_image_folder(p):
                    yield p2

    for f in go_log_image_folder(config['pic_outpath']):
        f = os.path.join(config['pic_outpath'], f, 'log')

        path_list = os.listdir(f)
        for p in path_list:
            log_file = os.path.join(f, p)
            if os.path.isfile(log_file):

                new_log_file = log_file.replace(config['pic_outpath'], config['pic_inpath'])
                try:
                    os.makedirs(os.path.split(new_log_file)[0])
                except:
                    pass

                log.info('move log file {} >> {}'.format(log_file, new_log_file))
                os.rename(log_file, new_log_file)



if __name__ == '__main__':
    log.info('main func start>>>>>>>>>>>>>>>>>>>>>>')
    # 获取所有待处理的日志文件列表
    all_log_file_path_list = []

    if True:
        def go_log_image_folder(folder):
            if not os.path.isdir(folder):
                return

            path_list = os.listdir(folder)
            if set(path_list) == set(['image', 'log']):
                if os.path.isdir(os.path.join(folder, 'image')) and os.path.isdir(os.path.join(folder, 'log')):
                    yield folder
                    return

            for p in path_list:
                p = os.path.join(folder, p)
                if os.path.isdir(p):
                    for p2 in go_log_image_folder(p):
                        yield p2

        dir_list = []
        with open(config['dir_list_file']) as f:
            while True:
                l = f.readline()
                if not l:
                    break
                l = l.strip()
                dir_list.append(l)

        for d in dir_list:
            for f in go_log_image_folder(d):
                f = os.path.join(d, f, 'log')

                path_list = os.listdir(f)
                for p in path_list:
                    file_path = os.path.join(f, p)
                    if os.path.isfile(file_path):
                        all_log_file_path_list.append(file_path)
                        log.info('add log file: {}'.format(file_path))

    all_log_file_path_list = sorted(list(set(all_log_file_path_list)))
    log.info('len(all_log_file_path_list) = {}'.format(len(all_log_file_path_list)))

    if True:
        if True:
            global sub_process_list
            sub_process_list = []

            signal.signal(signal.SIGTERM, on_main_process_exit)

            for task_id in range(config['worker_count']):
                p = Process(target=sub_process_func, args=(task_id, all_log_file_path_list,))
                p.start()
                sub_process_list.append( (task_id, p) )

            log.info('main process running...\nkill use >>>>>kill -SIGTERM {}'.format(os.getpid()))
            for (task_id, p) in sub_process_list:
                p.join()
        else:
            sub_process_func(0, ['/facepic/recognition/inpath/log_10.33.96.5/log/oa.log.2017-06-14'])


    log.info('main func safe exit!!!')
