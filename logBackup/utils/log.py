from datetime import datetime
import logging
import os

_DEBUG_LOGGER = logging.getLogger('debug')


def cur_timestamp():
    d = datetime.now()
    return d.strftime('%Y%m%d%H%M%S')


def cur_date():
    d = datetime.now()
    return '{0}{1}'.format(d.year, d.month)


def get_logger():
    global LOGGER
    return LOGGER


def get_filename(root, sub_log_folder, log_name='debug'):
    file_fields = [log_name]
    file_fields.append(cur_date())
    filename = '_'.join(file_fields) + '.log'

    log_dir_path = os.path.join(root, 'log', sub_log_folder)
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path, exist_ok=True)

    return os.path.join(root, log_dir_path, filename)


def setup(root, sub_log_folder, log_name, level=logging.DEBUG, console=True):
    global _DEBUG_LOGGER
    filename = get_filename(root, sub_log_folder, log_name)
    file_handler = logging.FileHandler(filename, mode='a', encoding='utf-8',
                                       delay=False)
    console_handler = logging.StreamHandler()
    log_format = '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s'
    debug_formatter = logging.Formatter(log_format)
    file_handler.setFormatter((debug_formatter))

    if not level:
        _DEBUG_LOGGER.setLevel(logging.DEBUG)
    else:
        _DEBUG_LOGGER.setLevel(level)

    _DEBUG_LOGGER.handlers = []
    _DEBUG_LOGGER.addHandler(file_handler)

    if console:
        _DEBUG_LOGGER.addHandler(console_handler)
