from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from logBackup import config


def get_session(db_url=None):
    if not db_url:
        db_url = 'postgresql://{}:{}@{}:{}/{}'.format(
            config.ccm.user, config.ccm.password, config.ccm.ip,
            config.ccm.port, config.ccm.db
        )
    engine = create_engine(db_url)
    sessions = scoped_session(sessionmaker(bind=engine))
    return sessions


session = get_session()
