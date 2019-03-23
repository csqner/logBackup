import json

from logBackup.utils.salt import Salt
from logBackup.utils.exceptions import SaltClientError
from logBackup.config import Backup
from logBackup.utils.log import get_logger

logger = get_logger()


class SaltClient(Salt):
    def __init__(self, host, **kwargs):
        self.host = host
        self.salt_api = None
        super().__init__(host, **kwargs)

    def run(self, payload):
        logger.info('try to invoke salt api')
        result = super().run(self.salt_api, payload)
        if result['message'] != 'OK':
            raise SaltClientError('fail')
        return result


class FsClient(SaltClient):
    def __init__(self, host, **kwargs):
        self.salt_api = 'fs'
        super().__init__(host, **kwargs)

    def backup_log(self, source, target, user, identity, start, end):
        action = 'backup'
        log_backup_timeout = Backup.log_backup_timeout

        params = dict(
            user=user, identity=identity, start=start, end=end,
            timout=log_backup_timeout, source=source, target=target
        )
        payload = dict(action=action, params=params)
        logger.info('payload: {}'.format(payload))
        return self.run(payload)

    def relocate_backupset(self, source, target, user):
        action = 'reloacate'
        params = dict(source=source, target=target, user=user)
        payload = dict(action=action, params=params)
        logger.info('payload: {}'.format(payload))
        return self.run(payload)


class LogCheck(SaltClient):
    def __init__(self, host, **kwargs):
        super().__init__(host, **kwargs)
        self.salt_api = 'logCheck'

    def check_increment(self, last_bkfile_mtime, first_time, db_type,
                        source_path):
        action = 'check_increment'
        params = dict(last_bkfile_mtime=last_bkfile_mtime,
                      first_time=first_time,
                      db_type=db_type, source_path=source_path)
        payload = dict(action=action, params=params)
        logger.info('payload: {}'.format(payload))
        result = self.run(payload)
        return result

    def check_expire(self, source_path, end_date):
        action = 'check_expire'
        params = dict(source_path=source_path, end_date=end_date)
        payload = dict(action=action, params=params)
        logger.info('payload: {}'.format(payload))
        result = self.run(payload)
        return result
