import datetime

from definition import ROOT_DIR

ERROR_LOG_FILENAME = ROOT_DIR + f'/logs/app-{datetime.datetime.now(datetime.timezone.utc).date()}.log'

LOGGING_CONFIG = {
    "version": 1,
   # "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": '[%(asctime)s | %(levelname)s] - %(module)s: %(message)s',
           # "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # "json": {
        #     "()": "pythonjsonlogger.jsonlogger.JsonFormatter",  # The class to instantiate!
        #     "format": """
        #      asctime: %(asctime)s
        #      created: %(created)f
        #      filename: %(filename)s
        #      funcName: %(funcName)s
        #      levelname: %(levelname)s
        #      levelno: %(levelno)s
        #      lineno: %(lineno)d
        #      message: %(message)s
        #      module: %(module)s
        #      msec: %(msecs)d
        #      name: %(name)s
        #      pathname: %(pathname)s
        #      process: %(process)d
        #      processName: %(processName)s
        #      relativeCreated: %(relativeCreated)d
        #      thread: %(thread)d
        #      threadName: %(threadName)s
        #      exc_info: %(exc_info)s
        #  """,
        #     "datefmt": "%Y-%m-%d %H:%M:%S",
        # },
    },
    "handlers": {
        "logfile-rotate": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": ERROR_LOG_FILENAME,
            "backupCount": 10,  # Param for class above. Defines how many log files to keep as it grows
            "maxBytes": 5*10**6,
            "mode": "a"
        },
        "logfile": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": ERROR_LOG_FILENAME,
            "mode": "a"
        },
        "stdout": {
            "formatter": "default",
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Param for class above. It means stream to console
        },
        # "json": {
        #     "formatter": "json",
        #     "class": "logging.StreamHandler",  # OUTPUT: Same as above, stream to console
        #     "stream": "ext://sys.stdout",
        # },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": []
        },
    },
    "root": {
        "level": "WARN",
        "handlers": [
            "logfile-rotate",
            "stdout"
            # "json"
        ]
    },
}