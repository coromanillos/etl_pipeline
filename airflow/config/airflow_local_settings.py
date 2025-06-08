# config/airflow_local_settings.py

from pythonjsonlogger import jsonlogger
import logging
import sys

formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s',
    json_ensure_ascii=False
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

for logger_name in (
    'airflow', 'airflow.task', 'airflow.task_runner', 'airflow.jobs.scheduler_job'
):
    airflow_logger = logging.getLogger(logger_name)
    airflow_logger.handlers.clear()
    airflow_logger.setLevel(logging.INFO)
    airflow_logger.addHandler(handler)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'json_ensure_ascii': False
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'airflow': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.task': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.task_runner': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.jobs.scheduler_job': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
