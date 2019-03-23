import datetime
import time
import uuid
import os
from functools import wraps

from logBackup.config import DB
from logBackup.utils.exceptions import (ParamError, SaltClientError,
                                        SaltParamError, SaltError, SaltCmdError)


def session_remove(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


def get_datetime():
    return datetime.datetime.now()


def int_to_datetime(year, month, day, hour, minute, second):
    date_time = datetime.datetime.strptime(
        '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second),
        '%Y-%m-%d %H:%M:%S')
    return date_time


def datetime_to_time_time_str(date_time):
    return str(time.mktime(date_time.timetuple()))


def datetime_to_datetime_str(date_time):
    return date_time.strftime('%Y-%m-%d %H:%M:%S')


def time_str_to_datetime(time_str):
    return datetime.datetime.fromtimestamp(float(time_str))


def gen_task_name():
    return str(uuid.uuid1())


def get_base_info(instance_name=None, db_type=None, timestp='19700101',

                  port=3306, mysql_info=None):
    if db_type == 'DBT:P':
        source_path = os.path.join(DB.postgres.source_archlog_path,
                                   instance_name)
        target_path = os.path.join(os.path.join(DB.ma_mount_point,
                                                DB.postgres.backup_sub_dir),
                                   timestp)
        user = DB.postgres.user
        identity = ':'.join([instance_name, port])
    elif db_type == 'DBT:MG':
        source_path = os.path.join(DB.mongodb.source_archlog_path,
                                   instance_name)
        target_path = os.path.join(
            os.path.join(DB.ma_mount_point, DB.mongodb.backup_sub_dir), timestp)
        user = DB.mongodb.user
        identity = ':'.join([instance_name, port])
    elif db_type == 'DBT:MY':
        if not mysql_info:
            raise ParamError('mysql info null')
        if mysql_info.get('db_role')[-1].lower() == 'p':
            role = 'primary'
        else:
            role = 'local'
        dir_name = '_'.join(mysql_info.get('site_code'), role, instance_name)
        source_path = os.path.join(
            os.path.join(DB.mysql.source_archlog_path, dir_name), timestp)
        target_path = os.path.join(DB.ma_mount_point, DB.mysql.backup_sub_dir)
        user = DB.mysql.user
        identity = ':'.join([instance_name, port])
    else:
        raise ParamError('error')
    return dict(source_path=source_path, target_path=target_path, user=user,
                identity=identity)


def get_db_type_for_str(db_type):
    if db_type == 'DBT:MG':
        return 'mongodb'
    elif db_type == 'DBT:P':
        return 'postgresql'
    elif db_type == 'DBT:MY':
        return 'mysql'


def gen_end_date(date, retention_day):
    date = date - datetime.timedelta(days=retention_day)
    end_date = date.strftime('%Y%m%d')
    return end_date


def retry(nums=3, interval=5):
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            count = 0
            while count < nums:
                try:
                    ret = func(*args, **kwargs)
                    return ret
                except (ParamError, SaltCmdError, SaltParamError, SaltError,
                        SaltClientError, Exception):
                    count += 1
                time.sleep(interval)
            raise Exception('retry')

        return inner

    return wrap
