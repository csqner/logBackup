class ccm:
    user = 'test'
    password = 'test'
    ip = 'localhost'
    db = 'test'
    port = 3307


class salt:
    server_addr = 'http://localhost:2345'
    timeout = 10 * 100
    role = 'test'
    user = 'test'


class DB:
    ma_mount_point = '/data/backup'

    class postgres:
        user = 'postgres'
        group = 'postgres'
        source_archlog_path = '/data/postgres'
        backup_sub_dir = 'postgres'

    class mysql:
        user = 'mysql'
        group = 'mysql'
        source_archlog_path = '/data/mysql'
        backup_sub_dir = 'mysql'

    class mongodb:
        user = 'mongodb'
        group = 'mongodb'
        source_archlog_path = '/data/mongodb'
        backup_sub_dir = 'mongodb'


class Backup:
    log_backup_timeout = 300
    start_wwal_location_timeout_ldg = 60
    schedule_interval = 30


class DeleteLog:
    schedule_crontab = '23:30'


class CeleryInfo:
    broker_url = 'redis://localhost:6379/1'
    result_backend = 'redis://localhost:6379/1'
    result_expires = 60 * 60 * 24 * 3
    enable_utc = False
    timezone = 'Asia/Shanghai'
    task_default_queue = 'logBackup'
    task_default_exchange = 'logBackup'
    task_default_routing_key = 'logBackup'
