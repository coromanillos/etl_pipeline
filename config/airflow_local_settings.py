# config/airflow_local_settings.py

from pythonjsonlogger import jsonlogger
import logging

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d %(message)s",
            json_ensure_ascii=False
        )

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            "()": CustomJsonFormatter,
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "task": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },

    "loggers": {
        "airflow": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "airflow.task": {"handlers": ["task"], "level": "INFO", "propagate": False},
        "airflow.task_runner": {"handlers": ["task"], "level": "INFO", "propagate": False},
    },

    "root": {"handlers": ["console"], "level": "INFO"},
}
