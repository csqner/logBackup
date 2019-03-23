from . import flask_app
from .view import Schedule, Test, Version


class URL:
    _prefix = '/backup/log/api/v1/'
    test = _prefix + 'test/'
    version = _prefix + 'version/'
    schedule = _prefix + 'schedule/'


flask_app.add_url_rule(URL.schedule, view_func=Schedule.as_view('schedule'))
flask_app.add_url_rule(URL.schedule + '<entity_name>/',
                       view_func=Schedule.as_view('schedules'))
flask_app.add_url_rule(URL.test, view_func=Test.as_view('test'))
flask_app.add_url_rule(URL.version, view_func=Version.as_view('version'))
