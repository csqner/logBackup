import glob
import json
import sys
import argparse
from datetime import datetime
import os
import logging
import math

import errno
import signal
from functools import wraps

app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(app_root)


class Argparse:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='log check utils'
        )
        self.parser.add_argument('--json', help='json data')
        self.args = self.parser.parse_args()


class RunCommandError(Exception):
    """"""


class TimeOutError(Exception):
    """"""


def timeout(seconds, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeOutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def cur_date():
    d = datetime.now()
    return '{0}{1}'.format(d.year, d.month)


def cur_timestamp():
    d = datetime.now()
    return d.strftime('%Y%m%d%H%M%S')


def fetch_log_file(root, base_name):
    sub_log_folder = cur_date()
    log_dir_path = os.path.abspath(os.path.join(root, 'log/', sub_log_folder))

    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)

    log_file = os.path.join(log_dir_path, base_name)
    return log_file


def get_logger():
    global LOGGER
    return LOGGER


def setup_logger(root, base_name, level=logging.DEBUG):
    global LOGGER
    filename = fetch_log_file(root, base_name)
    file_handler = logging.FileHandler(filename, mode='a', encoding='utf-8',
                                       delay=False
                                       )
    log_format = '%(asctime)s %(levelname)s:%(message)s'
    debug_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(debug_formatter)

    LOGGER.setLevel(level)
    LOGGER.addHandler(file_handler)


def str_to_json(exec_cmd_is_success=True, descriptions=None):
    if not descriptions:
        descriptions = {}
    if exec_cmd_is_success:
        rs = {'message': 'OK', 'code': 200, 'descriptions': descriptions}
        json_data = json.dumps(rs)
        logging.info('return: {}'.format(json_data))
        sys.exit(0)
    rs = {'message': 'ERROR', 'code': 500, 'descriptions': descriptions}
    json_data = json.dumps(rs)
    logging.error('return: {}'.format(json_data))
    sys.exit(1)


def check_source(source_path):
    if not os.path.exists(source_path):
        raise KeyError('path {} not exists'.format(source_path))
    return True


@timeout(20)
def check_increment(source_path, last_bkfile_mtime, first_time, db_type):
    check_source(source_path)
    if first_time == 1 or first_time == '1':
        flag = True
    elif first_time == 0 or first_time == '0':
        flag = False
    else:
        raise KeyError('first time invalid')

    if db_type == 'DBT:MG' or db_type == 'DBT:P':
        glob_files = glob.iglob(os.path.join(source_path, '*'))
    elif db_type == 'DBT:MY':
        glob_files = glob.iglob(os.path.join(source_path, 'mysql-bin.*'))

    all_files = []
    for i in glob_files:
        all_files.append(i)

    all_files = sorted(all_files, key=lambda  x: os.path.getmtime(x))

    if flag:
        new_all_files = all_files
    else:
        new_list = []
        try:
            modify_timess = float(last_bkfile_mtime)
        except Exception:
            raise KeyError('last back mtime error')

        for tmp in all_files:
            if os.path.getmtime(tmp) > modify_timess:
                new_list.append(tmp)

        new_all_files = new_list

    files = []
    for file in new_all_files:
        tmp = dict(file=os.path.basename(file),
                   modify_time=str(os.path.getmtime(file)),
                   size_mb=str(math.ceil(os.path.getsize(file)/1024/1024))
                   )
        files.append(tmp)
    return files


@timeout(20)
def check_expire_log(source_path, end_date):
    check_source(source_path)
    files = []
    glob_files = glob.iglob(
        os.path.join(source_path, '[0-9]'*8)
    )
    for file in glob_files:
        base_file_float_name = os.path.basename(file)
        if int(base_file_float_name) <= end_date:
            files.append(base_file_float_name)
    return files


def main():
    arg_obj = Argparse()
    args = arg_obj.args

    if args.json:
        logging.info('accept: []'.format(args.json))
        param = json.loads(args.json)

        try:
            action = param['action']
            params = param['params']
            if action == 'check_increment':
                last_bkfile_mtime = params['last_bkfile_mtime']
                first_time = params['first_time']
                db_type = params['db_type']
                source_path = params['source_path']
                files = check_increment(source_path, last_bkfile_mtime,
                                        first_time, db_type)
            elif action == 'check_expire_log':
                source_path = params['source_path']
                end_date = int(params['end_date'])
                files = check_expire_log(source_path, end_date)
            else:
                raise KeyError('action error')

            str_to_json(True, files)
        except KeyError as e:
            logging.error('params error: {}'.format(e.message))
            str_to_json(False, 'params error')
        except Exception as e:
            logging.error('params error: {}'.format(e.message))
            str_to_json(False, e.message)
    else:
        str_to_json(False, 'no args')



if __name__ == '__main__':
    LOGGER = logging.getLogger('debug')
    file_base_name = 'log_check_{}.log'.format(cur_date())
    setup_logger(app_root, file_base_name)
    logger = get_logger()
    main()