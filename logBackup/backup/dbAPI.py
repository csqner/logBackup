import datetime

from logBackup.utils.dbSession import session
from logBackup.utils.exceptions import ParamError
from logBackup.backup.model import LogBackupRecord, LogSchedule
from logBackup.utils.tools import (get_datetime, time_str_to_datetime,
                                   datetime_to_datetime_str)


def get_host(instance_name, db_type, db_role=None):
    if db_type == 'DBT:MG':
        sql = ("select host from ccm_host where instance_name = {}".format(
            instance_name))
    elif db_type == 'DBT:P' or db_type == 'DBT:MY':
        sql = ("select host from ccm_host where"
               " instance_name = {} and db_role = {}".format(instance_name,
                                                             db_role))
    else:
        raise ParamError('error')
    result = session.execute(sql).fetchall()
    session.commit()
    host = ''
    if result:
        host = result[0][0]
    return host


def get_active_schedule(min_time=None, max_time=None, cur=None):
    sql = ("select * from xxx")
    result = session.execute(sql)
    session.commit()
    items = []
    for item in result:
        next_run_time = item[9]
        if not next_run_time:
            items.append(item)
        elif next_run_time <= cur:
            items.append(item)
    return items


def get_all_schedule():
    sql = ("select * from xxx")
    result = session.execute(sql)
    session.commit()
    return result


def get_one_schedule(entity_name):
    sql = ("select * from xxx where entity_name = {}".format(entity_name))
    result = session.execute(sql).fetchall()
    session.commit()
    items = []
    for item in result:
        if item[5]:
            last_bkfile_mtime = datetime_to_datetime_str(item[5])
        if item[6]:
            next_run_time = datetime_to_datetime_str(item[6])
        schedule = dict(id_st_bk_dblog_schedule=item[0],
                        id_st_backup_policy=item[1],
                        entity_name=item[2], logbk_interval_min=item[3],
                        schedule_status=item[4],
                        last_bkfile_mtime=last_bkfile_mtime,
                        next_run_time=next_run_time
                        )
        items.append(schedule)
    return items


def filter_schedule_and_host(items):
    new_items = []
    tmp_instance_name = set()
    for item in items:
        db_type, entity_name = item[2], item[3]
        instance_name, instance_id = item[4], item[0]
        db_role = item[6]

        if instance_name in tmp_instance_name:
            continue

        if db_type == 'DBT:P':
            sql = (
                "select * in xxx1 where entity like '%{}%'".format(entity_name))
        elif db_type == 'DBT:MY':
            sql = (
                "select * in xxx2 where entity like '%{}%'".format(entity_name))
        elif db_type == 'DBT:MG':
            sql = (
                "select * in xxx3 where entity like '%{}%'".format(entity_name))
        else:
            continue

        result = session.execute(sql).fetchall()
        session.commit()

        if not result:
            continue

        try:
            host = get_host(instance_name, db_type, db_role)
        except Exception:
            continue

        if len(result[0]) >= 2:
            if result[0][1] == instance_id:
                new_items.append(list(item) + [host])
                tmp_instance_name.add(instance_name)
        else:
            if instance_name == result[0][0]:
                new_items.append(list(item) + [host])
    return new_items


def get_schedule(min_time=None, max_time=None, cur=None):
    if min_time and max_time and cur:
        items = get_active_schedule(min_time, max_time, cur)
    else:
        items = get_all_schedule()
    result = filter_schedule_and_host(items)
    return result


def update_next_run_time(schedule_id, interval):
    next_run_time = get_datetime() + datetime.timedelta(minutes=interval)
    session.query(LogSchedule).filter(
        LogSchedule.id_st_bk_dblog_schedule == schedule_id
    ).update({'next_run_time': next_run_time})


def update_last_bkfile_mtime(schedule_id, last_bkfile_mtime):
    session.query(LogSchedule).filter(
        LogSchedule.id_st_bk_dblog_schedule == schedule_id
    ).update({'last_bkfile_mtime': time_str_to_datetime(last_bkfile_mtime)})


def update_record(record_id, data):
    session.query(LogBackupRecord).filter(
        LogBackupRecord.id_st_bk_dblog_set == record_id
    ).update(data)


def update_schedule(params):
    id_st_bk_dblog_schedule = params.pop('id_st_bk_dblog_schedule')
    session.query(LogSchedule).filter(
        LogSchedule.id_st_bk_dblog_schedule == id_st_bk_dblog_schedule
    ).update(params)
    session.commit()


def update_interval(id_db_backup_policy, logbk_interval_min):
    sql = ("update xxx set logbk_interval_min = "
           "{0} where id_db_backup_policy = {1}".format(logbk_interval_min,
                                                        id_db_backup_policy))
    session.execute(sql)
    session.commit()


def insert_schedule(params):
    new_policy = LogSchedule(**params)
    session.add(new_policy)
    session.commit()
    return new_policy.id_st_bk_dblog_schedule
