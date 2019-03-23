import os
import json

from flask import request
from flask.views import MethodView

from . import flask_app
from logBackup.utils.dbSession import session
from logBackup.backup.dbAPI import (insert_schedule, update_interval,
                                    get_one_schedule, update_schedule)
from logBackup.utils.log import get_logger, setup
from logBackup.utils.exceptions import ParamError
from logBackup.config import VERSION

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
setup(project_root, 'webapp', 'app')
logger = get_logger()


@flask_app.after_request
def flask_cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Methods'] = '*'
    environ.headers[
        'Access-Control-Allow-Headers'] = 'x-requested-with, content-type'
    environ.headers['Content-Type'] = 'application/json'
    return environ


@flask_app.teardown_appcontext
def cleanup(*args):
    session.remove()


@flask_app.errorhandler(Exception)
def exception_handler(e):
    logger.error(e)
    result = dict(msg='unknown error')
    code = 500
    return http_msg(result, code)


@flask_app.errorhandler(404)
def api_not_found(e):
    logger.error('unknown api')
    result = dict(msg='unknown api')
    code = 404
    return http_msg(result, code)


def http_msg(result=None, code=None):
    if 200 <= code <= 399:
        result = dict(msg=result or 'success', code=code)
    if isinstance(result, dict):
        result = json.dumps(result)
    return result, code


class Test(MethodView):
    def get(self):
        result = dict(status='success')
        return http_msg(result, 200)


class Version(MethodView):
    def get(self):
        result = dict(version=VERSION)
        return http_msg(result, 200)


class Schedule(MethodView):
    def get(self, entity_name):
        logger.info('query entity {}'.format(entity_name))
        result = get_one_schedule(entity_name)
        return http_msg(result, 200)

    def put(self):
        params = request.json
        if params.get('id_db_backup_policy') and params.get(
                'logbk_interval_min'
        ):
            id_db_backup_policy = params.pop('id_db_backup_policy')
            logbk_interval_min = params.pop('logbk_interval_min')
            update_interval(id_db_backup_policy, logbk_interval_min)
            logger.info('update interval id {}'.format(id_db_backup_policy))

        if params.get('id_st_bk_dblog_schedule'):
            update_schedule(params)
            logger.info('update schedule id {}'.format(
                params.get('id_st_bk_dblog_schedule')))
        return http_msg()

    def post(self):
        params = request.json
        if not params.get('logbk_interval_min') and not params.get(
                'id_db_backup_policy'):
            raise ParamError('params error')

        logbk_interval_min = params.pop('logbk_interval_min')
        id_db_backup_policy = params.pop('id_db_backup_policy')
        params['id_st_backup_policy'] = id_db_backup_policy
        schedule_id = insert_schedule(params)
        logger.info('insert schedule id {}'.format(schedule_id))

        if logbk_interval_min and id_db_backup_policy:
            update_interval(id_db_backup_policy, logbk_interval_min)
            logger.info('update interval id {}'.format(id_db_backup_policy))

        result = dict(id_st_bk_dblog_schedule=schedule_id)
        return http_msg(result, 200)
