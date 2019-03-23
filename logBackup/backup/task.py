import os

from logBackup.utils.tools import (retry, get_base_info, get_datetime,
                                   gen_end_date, time_str_to_datetime,
                                   get_db_type_for_str)
from logBackup.utils.log import setup, get_logger
from logBackup.utils.exceptions import ParamError, SaltClientError
from logBackup.utils.saltops import LogCheck, FsClient
from logBackup.backup.model import LogBackupRecord
from logBackup.utils.dbSession import session
from logBackup.backup.dbAPI import update_last_bkfile_mtime, update_record

__all__ = ['task_find_increment_files', 'task_find_expire_files',
           'task_backup_log', 'task_delete_log']

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
setup(project_root, 'task', 'task')
logger = get_logger()


@retry(3, 5)
def task_find_increment_files(host, last_bkfile_mtime, next_run_time, db_type,
                              instance_name, mysql_info=None):
    first_time = 1
    if next_run_time:
        first_time = 0

    try:
        info = get_base_info(instance_name, db_type, mysql_info=mysql_info)
    except ParamError:
        logger.error('instance error')
        return dict(files=[])

    source_path = info.get('source_path')
    ci = LogCheck(host)

    try:
        result = ci.check_increment(last_bkfile_mtime, first_time, db_type,
                                    source_path)
    except (SaltClientError, Exception)  as e:
        logger.error('check log error, run again')
        raise Exception(e.message)
    logger.info('find files')
    return dict(files=result, host=host)


@retry(3, 5)
def task_find_expire_files(host, db_type, instance_name, retention_day,
                           mysql_info=None):
    try:
        info = get_base_info(instance_name, db_type, mysql_info=mysql_info)
    except ParamError:
        logger.error('params error')
        return dict(files=[])

    target_path = os.path.dirname(info.get('target_path'))
    ci = LogCheck(host)
    cur = get_datetime()
    end_date = gen_end_date(cur, retention_day)

    try:
        result = ci.check_expire(target_path, end_date)
    except (SaltClientError, Exception) as e:
        logger.error('check expire error, run aggin')
        raise Exception(e.message)
    logger.info('find files')
    return dict(files=result, host=host)


def task_delete_log(files, port, db_type, instance_name, timestamp,
                    mysql_info=None, host=None):
    if not files:
        return None
    try:
        info = get_base_info(instance_name, db_type, timestamp, port,
                             mysql_info)
    except Exception:
        logger.error('get base info error')
        return None
    backup_host = host or files.get('host')
    expire_files = files.get('files')
    target_path = info.get('target_path')
    delete_files = [os.path.join(target_path, files) for file in expire_files]
    user = info.get('user')

    @retry(3, 4)
    def _delete(source, target, user, timestamp, instance_name, db_type, host):
        fs = FsClient(host)
        fs.relocate_backupset(source, target, user, timestamp, instance_name,
                              db_type)

    for file in delete_files:
        source = file
        db_type_new = get_db_type_for_str(db_type)
        base = os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(target_path)))
        ))
        target = os.path.join(base, instance_name)
        try:
            _delete(source, target_path, user, timestamp, db_type_new,
                    backup_host)
        except Exception:
            logger.error('delete error')


def task_backup_log(files, port, db_type, instance_name, timestamp,
                    mysql_info=None, host=None, schedule_id=None,
                    task_name=None):
    if not files.get('files'):
        logger.error('not files error')
        return None
    try:
        info = get_base_info(instance_name, db_type, timestamp, port,
                             mysql_info)

    except Exception:
        logger.error('get base info error')
        return None

    start = files.get('files')[0].get('file')
    end = files.get('files')[-1].get('file')
    backup_host = host or files.get('host')
    source_path, target_path = info['source_path'], info['target_path']
    user, identity = info.get('user'), info.get('identity')
    record_items = []
    cur_time = get_datetime()

    for item in files.get('file'):
        file_name, size_mb = item.get('file'), int(item.get('size_mb'))
        file_mtime = time_str_to_datetime(item.get('modify_time'))
        source_file = os.path.join(source_path, file_name)
        target_file = target_path
        data = dict(backup_status='execute',
                    backup_start_time=cur_time, task_name=task_name,
                    size_mb=size_mb, file_create_time=file_mtime,
                    source_file=source_file, target_file=target_file)
        if schedule_id:
            data = dict(id_st_dblog_schedule=schedule_id,
                        backup_start_time=cur_time, backup_status='execute',
                        size_mb=size_mb, file_create_time=file_mtime,
                        source_file=source_file, target_file=target_file)
        record_items.append(LogBackupRecord ** data)
    session.add_all(record_items)

    session.commit()
    record_ids = [record.id_st_bk_dblog_set for record in record_items]
    if schedule_id:
        last_bkfile_mtime = files.get('files')[-1].get('modify_time')
        update_last_bkfile_mtime(schedule_id, last_bkfile_mtime)
    logger.info('backup start')

    @retry(3, 4)
    def _backup(source_path, target_path, user, identity, start, end, host):
        fs = FsClient(host)
        fs.backup_log(source_path, target_path, user, identity, start, end)

    try:
        _backup(source_path, target_path, user, identity, start, end,
                backup_host)
    except Exception:
        logger.error('backup error')
        cur_time = get_datetime()
        for record_id in record_ids:
            data = dict(backup_status='fail', backup_end_time=cur_time)
            update_record(record_id, data)
        session.commit()
        return None

    cur_time = get_datetime()
    for record_id in record_ids:
        data = dict(backup_status='success', backup_end_time=cur_time)
        update_record(record_id, data)
    session.commit()