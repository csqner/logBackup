import celery
from celery.schedules import crontab

from logBackup.celerySchedule.celeryApp import celery_app
from logBackup.config import Backup, DeleteLog
from logBackup.utils.exceptions import FileNull
from logBackup.backup.dbAPI import *
from logBackup.utils.log import get_logger, setup
from logBackup.utils.tools import *
from logBackup.backup.task import *

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
setup(project_root, 'schedule', 'schedule')
logger = get_logger()


class BaseTask(celery.Task):
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        session.remove()


class ScheduleBackup(BaseTask):
    def on_success(self, retval, task_id, args, kwargs):
        logger.info('backup end')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, SaltClientError):
            logger.error('salt client error, {}'.format(einfo))
        elif isinstance(exc, FileNull):
            logger.info('file nul')
        elif isinstance(exc, ParamError):
            logger.error('params error')
        elif isinstance(exc, KeyError):
            logger.error('params error')
        else:
            logger.error('unknown error')


@celery_app.task
def test():
    return dict(status='success')


@celery_app.task(base=BaseTask)
def schedule_backup():
    logger.info('schedule backup start')
    cur = get_datetime()
    max_time = int_to_datetime(cur.year, cur.month, cur.day, cur.hour,
                               cur.minute, 59)
    min_time = int_to_datetime(cur.year, cur.month, cur.day, cur.hour,
                               cur.minute, 0)
    items = get_schedule(min_time, max_time, cur)
    for item in items:
        port, db_type, schedule_id = item[5], item[2], item[11]
        host, interval, instance_name = item[12], item[8], item[4]
        timestamp = cur.stftime('%Y%m%d')

        if not host:
            logger.error('host not found')
            continue

        mysql_info = dict()
        last_bkfile_mtime = ''
        next_run_time = ''
        if db_type == 'DBT:MY':
            mysql_info = dict(site_code=item[7], db_role=item[6])
        if item[10]:
            last_bkfile_mtime = datetime_to_time_time_str(item[10])
        if item[9]:
            next_run_time = item[9]

        chain = find_increment_files.s(host, last_bkfile_mtime, next_run_time,
                                       db_type, instance_name, mysql_info
                                       ) | backup_log.s(port, db_type,
                                                        instance_name, timestamp,
                                                        mysql_info,
                                                        schedule_id = schedule_id)
        chain()

        logger.info('execute job backup')

        update_next_run_time(schedule_id, interval)

    session.commit()
    logger.info('schedule backup end')


@celery_app.task(base=BaseTask)
def schedule_delete():
    logger.info('schedule delete start')
    cur = get_datetime()
    items = get_schedule()
    for item in items:
        port, db_type, schedule_id = item[5], item[2], item[11]
        host, interval, instance_name = item[12], item[8], item[4]
        retention_day = item[12] or 30
        timestamp = cur.strftime('%Y%m%d')

        if not host:
            logger.info('host not found')
            continue

        mysql_info = dict()
        if db_type == 'DBT:MY':
            mysql_info = dict(site_code=item[7], db_role=item[6])

        chain = find_expire_files.s(host, db_type, instance_name, retention_day,
                                    mysql_info) | delete_log.s(port, db_type,
                                                               instance_name,
                                                               timestamp,
                                                               mysql_info)
        chain()

        logger.info('execute schedule delete job')
    logger.info('schedule delete end')


@celery_app.task(base=BaseTask)
def find_increment_files(host, last_bkfile_mtime, next_run_time, db_type,
                         instance_name, mysql_info=None):
    logger.info('find increment')
    result = task_find_increment_files(host, last_bkfile_mtime, next_run_time,
                                       db_type,
                                       instance_name, mysql_info)
    logger.info('find increment end')
    return result


@celery_app.task(base=BaseTask)
def find_expire_files(host, db_type, instance_name, retention_day,
                      mysql_info=None):
    logger.info('find expire start')
    result = task_find_expire_files(host, db_type, instance_name, retention_day,
                                    mysql_info)
    logger.info('find expire end')
    return result


@celery_app.task(base=ScheduleBackup)
def backup_log(files, port, db_type, instance_name, timestamp,
               mysql_info=None, host=None, schedule_id=None, task_name=None):
    logger.info('backup log start')
    result = task_backup_log(files, port, db_type, instance_name, timestamp,
                             mysql_info, host, schedule_id, task_name)
    logger.info('backup log end')
    return result


@celery_app.task(base=ScheduleBackup)
def delete_log(files, port, db_type, instance_name, timestamp,
               mysql_info=None, host=None):
    logger.info('delete log start')
    result = task_delete_log(files, port, db_type, instance_name, timestamp,
                             mysql_info, host)
    logger.info('delete log end')
    return result


celery_app.conf.beat_schedule = {
    'backup-log-schedule': {
        'task': 'logBackup.celerySchedule.celeryTask.schedule_backup',
        'schedule': Backup.schedule_interval
    },

    'delete-log-schedule': {
        'task': 'logBackup.celerySchedule.celeryTask.schedule_delete',
        'schedule': crontab(hour=int(DeleteLog.schedule_crontab.split(':')[0]),
                            minute=int(
                                DeleteLog.schedule_crontab.split(':')[1]))
    }
}
