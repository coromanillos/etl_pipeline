# config/airflow_local_settings.py

from pythonjsonlogger import jsonlogger

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'json_ensure_ascii': False,
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
