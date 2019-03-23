from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Prefix:
    created_date = Column(DateTime, default=datetime.now)
    created_by = Column(String(100))
    updated_date = Column(DateTime)
    updated_by = Column(String(100))


class LogSchedule(Base, Prefix):
    __tablename__ = 'schedule'

    id_st_bk_dblog_schedule = Column(Integer, primary_key=True)
    id_st_backup_policy = Column(Integer, nullable=False)
    schedule_status = Column(String(20), default='active')
    startup_time = Column(DateTime)
    last_bkfile_mtime = Column(DateTime)
    next_run_time = Column(DateTime)


class LogBackupRecord(Base, Prefix):
    __tablename__ = 'record'

    id_st_bk_dblog_set = Column(Integer, primary_key=True)
    id_st_bk_dblog_schedule = Column(
        ForeignKey('schedule.id_st_bk_dblog_schedule'), nullable=False)
    db_entity_id = Column(Integer)
    db_type = Column(String(5))
    db_instance_id = Column(Integer)
    source_file = Column(String(100))
    target_file = Column(String(100))
    file_create_time = Column(DateTime)
    db_internal_time = Column(DateTime)
    size_mb = Column(Integer)
    task_name = Column(String(100))
    backup_status = Column(String(24))
    backup_start_time = Column(DateTime)
    backup_end_time = Column(DateTime)


