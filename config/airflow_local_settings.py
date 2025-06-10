# config/airflow_local_settings.py

from pythonjsonlogger import jsonlogger
import logging

# Define a reusable JSON formatter class
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d %(message)s",
            json_ensure_ascii=False
        )

# Logging configuration dictionary
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
        }
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        "airflow": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "airflow.task": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "airflow.task_runner": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "airflow.jobs.scheduler_job": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    }
}
