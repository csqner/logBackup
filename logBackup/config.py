import os
from logBackup.utils.exceptions import ConfigError


env = os.environ.get('LOGBACKUPENV', 'TEST')


if env == 'DEV':
    from logBackup.configTest import *
elif env == 'TEST':
    from logBackup.configDev import *
else:
    raise ConfigError('env error')

VERSION = '0.1'