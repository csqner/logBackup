from celery import Celery

from logBackup.celerySchedule.celeryCfg import CONFIG

celery_app = Celery('LogTasks')
celery_app.config_from_object(CONFIG)