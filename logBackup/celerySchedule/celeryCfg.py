from logBackup.config import CeleryInfo


class BaseConfig(CeleryInfo):
    imports = ['logBackup.celerySchedule.celeryTask']


CONFIG = BaseConfig()
