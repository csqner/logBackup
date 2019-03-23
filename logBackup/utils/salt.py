import json
import requests
import time

from logBackup.config import salt
from logBackup.utils.exceptions import SaltError, SaltCmdError
from logBackup.utils.log import get_logger

logger = get_logger()


def url_join(*args):
    return '/'.join(args)


class Salt:
    def __init__(self, host, **kwargs):
        self.host = host
        self.role = kwargs.get('role', salt.role)
        self.user = kwargs.get('user')

        self.salt = salt.server_addr
        self.salt_timeout = int(salt.timeout)
        self.salt_api_header = {'Content-Type': 'application/json'}

    def get_payload(self, json_arg):
        return dict(
            target=self.host,
            args='-json' + '' + json.dumps(json_arg),
            role=self.role
        )

    def run(self, salt_interface, jsn):
        salt_api_url = url_join(self.salt, salt_interface)
        logger.debug('running salt')
        cmd_arg = json.dumps(jsn)
        data = dict(args='\\' + cmd_arg + '\\',
                    target=self.host, role=self.role)
        if self.user:
            data['user'] = self.user

        rsps = requests.post(salt_api_url, data)
        job_id = rsps.get('job_id')
        time_wait = 0
        while True:
            if time_wait > self.salt_timeout:
                raise SaltError('timeout')
            status = self.get_job_status(job_id)
            if status == 'running':
                time.sleep(3)
                time_wait += 3
            else:
                break

        job_return = self.get_cmd_result(job_id)
        return job_return

    def get_cmd_result(self, job_id):
        salt_api_url = url_join(self, salt, 'result')
        rsp = requests.post(
            salt_api_url,
            data={'args': job_id, 'target': self.host, 'role': self.role}
        )
        return rsp

    def job_status(self, job_id):
        salt_api_url = url_join(self, salt, 'status')
        rsp = requests.post(
            salt_api_url,
            data={'args': job_id, 'target': self.host, 'role': self.role}
        )
        return rsp
