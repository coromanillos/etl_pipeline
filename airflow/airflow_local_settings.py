# airflow_local_settings.py

import logging
import sys
from pythonjsonlogger import jsonlogger

def configure_logging():
    """
    Configure structured JSON logging for Airflow that integrates with
    stdout for Docker, and is ready for external log shippers (e.g., ELK, CloudWatch, S3).
    """
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        json_ensure_ascii=False
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Airflow-specific loggers
    for logger_name in (
        'airflow',
        'airflow.task',
        'airflow.task_runner',
        'airflow.jobs.scheduler_job',
    ):
        airflow_logger = logging.getLogger(logger_name)
        airflow_logger.handlers.clear()
        airflow_logger.setLevel(logging.INFO)
        airflow_logger.addHandler(handler)

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'json': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': 'ext://sys.stdout',
            }
        },
        'formatters': {
            'json': {
                '()': jsonlogger.JsonFormatter,
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            }
        },
        'root': {
            'handlers': ['json'],
            'level': 'INFO',
        },
        'loggers': {
            'airflow': {
                'handlers': ['json'],
                'level': 'INFO',
                'propagate': False,
            }
        }
    }

LOGGING_CONFIG = configure_logging()
