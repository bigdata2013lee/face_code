# encoding: utf-8
import base64
import os

# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  #开发环境的客户端字符集
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8' #生产环境的客户端字符集

import sys
if sys.version_info <= (3, 0):
    reload(sys)
    sys.setdefaultencoding('UTF8')

import logging.config
import uuid
from datetime import datetime
from multiprocessing import Process

import xlrd
import yaml
from PIL import Image
from sqlalchemy import create_engine

from util_tools import set_log_savepath, create_all_log_dirs, picture_util, check_card_code

try:
    from util_tools.db_password import get_db_password
except:
    pass

try:
    config = yaml.load(open('./config_files/laoshanlu.yaml', 'r', encoding='utf-8'))
except:
    config = yaml.load(open('./config_files/laoshanlu.yaml', 'r'))


config['pic_inpath'] = os.path.abspath(config['pic_inpath'])
config['pic_outpath'] = os.path.abspath(config['pic_outpath'])

log_config = yaml.load(open('logging.yaml', 'r'))
set_log_savepath(log_config, config['log_savepath'])
create_all_log_dirs(log_config)
logging.config.dictConfig(log_config)
log = logging.getLogger('log')

#读取UM账号与身份证的绑定关系
um_card_code_data = {}
book = xlrd.open_workbook(config['um_card_code_file'])
table = book.sheets()[0]
nrows = table.nrows
for i in range(nrows):
    r = table.row_values(i)
    if len(r) == 2:
        um_code, card_code = r
        check_result, check_msg = check_card_code(card_code)
        if check_result:
            # print(um_code, card_code)
            if isinstance(card_code, str):
                um_card_code_data[um_code] = card_code
            else:
                um_card_code_data[um_code] = str(card_code)

def sub_process_func(task_id, all_record_list): #子进程处理函数
    # 每个子进程定制日志目录
    for h in log_config['handlers']:
        if 'filename' in log_config['handlers'][h]:
            p1, p2 = os.path.split(log_config['handlers'][h]['filename'])
            log_config['handlers'][h]['filename'] = os.path.join(p1, 'task_{0}'.format(task_id), p2, )

    create_all_log_dirs(log_config)
    logging.config.dictConfig(log_config)
    create_all_log_dirs(log_config)

    pid=os.getpid()
    log.info('[{}][{}] sub_process_func start>>>>>>>>>>>>>>>>>>>>>>>>>'.format(task_id, pid))

    # 数据库连接池
    db_engine = create_engine(
        config['db']['uri'].format(password=config['db'].get('password') or get_db_password(config['db']['cyberark'])),
        pool_size=2,
        echo_pool=True,
        pool_recycle=3600
    )

    for record in all_record_list[task_id::config['worker_count']]:
        dest_image_list = []
        try:
            # camera_10/2017/09/27/-516611166.jpg,曾俊,C00000004679
            t = record.strip().split(',')
            org_ph_name = os.path.join(config['pic_inpath'], t[0])
            person_nm = t[1]
            um_code = t[2]

            card_code = um_card_code_data.get(um_code)
            if not card_code:
                log.warning('org_ph_name={} um_code={} no card_code'.format(org_ph_name, um_code))
                continue

            # 将图片移动到目的文件夹
            if not os.path.exists(org_ph_name):
                log.warning('org_ph_name={} um_code={} card_code={} file not exists!!!'.format(org_ph_name, um_code, card_code))
                continue

            photo_id = 'P_{}'.format(uuid.uuid1())
            pic_path = org_ph_name.replace(config['pic_inpath'], config['pic_outpath'])
            pic_path = os.path.join(os.path.split(pic_path)[0], photo_id+os.path.splitext(pic_path)[-1])
            try:
                os.makedirs(os.path.split(pic_path)[0])
            except:
                pass
            os.rename(org_ph_name, pic_path)
            dest_image_list.append( (pic_path, org_ph_name) )
            log.info('move file {} >>>> {}'.format(org_ph_name, pic_path))

            db_conn = db_engine.connect()
            with db_conn.begin() as db_trans:

                card_prov = int(card_code[:2])
                stat_month = datetime.today().date().replace(day=1)

                if sys.version_info >= (3, 0):
                    card_code = base64.b64encode(card_code.encode('utf8')).decode('utf8')
                else:
                    card_code = base64.b64encode(card_code)

                query_result = db_conn.execute(r'''
                        SELECT 
                            card_id
                        FROM facedata.fac_person_base_info  
                        WHERE card_code = :1 and card_prov = :2
                    ''', (
                    card_code, card_prov
                )).fetchall()

                # 人员基本信息表
                if query_result:
                    card_id = query_result[0][0]
                else:
                    card_id = 'H_' + str(uuid.uuid1())
                    card_type = '1'  # 身份证默认是1

                    db_conn.execute(r'''
                        insert into facedata.fac_person_base_info(
                          card_id,
                          card_code,
                          card_prov,
                          card_type,
                          person_nm
                        ) VALUES(:1, :2,:3, :4, :5)
                        ''', (
                        card_id,
                        card_code,
                        card_prov,
                        card_type,
                        person_nm
                    ))

                ph_path = os.path.split(pic_path)[0]
                ph_name = os.path.basename(pic_path)
                space_size = os.path.getsize(pic_path) / 1024  # 单位kb

                with Image.open(pic_path) as img:
                    pixel = '{}*{}'.format(img.size[0], img.size[1])
                    dpi = img.info.get('dpi') and '{}*{}'.format(*img.info['dpi'])
                    is_colour = picture_util.picture_is_colour(img)
                    data_source = '7'  # 崂山路考勤是7

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
                        ) VALUES(:1, :2,:3,:4,:5,:6,:7,:8,:9,:10, :11)
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
                        org_ph_name,
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

                log.info('image_path={} um_code={} card_code={} card_id={} photo_id={} file finish'.format(org_ph_name,
                                                                                                           um_code,
                                                                                                           card_code,
                                                                                                           card_id,
                                                                                                           photo_id))
        except:
            log.exception('process record={} exception!!!'.format(record))

            for (pic_path, org_ph_name) in dest_image_list:
                try:
                    os.rename(pic_path, org_ph_name)
                    log.info('[{}] rollback move file {} >>>> {}'.format(task_id, org_ph_name, pic_path))
                except:
                    pass

    log.info('[{}][{}] sub_process_func finish>>>>>>>>>>>>>>>>>>>>>>>>>'.format(task_id, pid))


if __name__ == '__main__':
    log.info('start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.')

    #读取识别记录文件
    all_record_list = []
    try:
        with open(config['camera_record_file'], encoding='utf-8') as f:
            while True:
                l = f.readline()
                if not l:
                    break
                all_record_list.append(l)
    except:
        with open(config['camera_record_file']) as f:
            while True:
                l = f.readline()
                if not l:
                    break
                all_record_list.append(l)

    log.info('len(all_record_list) = {} '.format(len(all_record_list)))

    if False:
        sub_process_list = []
        for task_id in range(config['worker_count']):
            p = Process(target=sub_process_func, args=(task_id, all_record_list,))
            p.start()
            sub_process_list.append(p)

        for sub_process in sub_process_list:
            sub_process.join()
    else:
        sub_process_func(0, all_record_list[2:3])

    log.info('main func safe exit!!!')
