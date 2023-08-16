import json
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = f"{BASE_DIR}/logs"
CONFIG = {}
try:
    with open(f"{BASE_DIR}/config/config.json", "r") as f:
        CONFIG = json.load(f)
except Exception as e:
    print(f"Error to load config from {BASE_DIR}/config/config.json")

MYSQL_CONFIG = CONFIG["mysql_db"]
MONGO_CONFIG = CONFIG["mongo_db"]
SERVER_INFO = CONFIG["server_info"]
SEARCH_ENGINE = CONFIG["search_engine"]
INTERNAL_EMAIL = CONFIG["internal_email"]
ALLOWED_HOSTS = SERVER_INFO["allow_hosts"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if MYSQL_CONFIG:
    for db_name, db_data in MYSQL_CONFIG.items():
        db_data.update({
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
            'TEST': {
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            }
        })
        DATABASES.update({
            db_name: db_data
        })
if MONGO_CONFIG:
    for db_name, db_data in MONGO_CONFIG.items():
        DATABASES.update({
            db_name: {
                'ENGINE': 'djongo',
                'ENFORCE_SCHEMA': False,
            }
        })

DATABASE_ROUTERS = ['chimera.db_router.DbRouter']
LOG_CONFIG = SERVER_INFO["log"]
SERVICE_NAME = LOG_CONFIG["service_name"]
DEBUG_LOG = LOG_CONFIG.get("log_debug", False)
DEBUG = SERVER_INFO.get("debug", False)
CACHE = CONFIG["cache"]
CONFIG_VARIABLE_TIMEOUT = 60 * 60 * 24 * 365
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = INTERNAL_EMAIL["host"]
EMAIL_USE_TLS = INTERNAL_EMAIL["use_tls"]
EMAIL_PORT = INTERNAL_EMAIL["port"]
EMAIL_HOST_USER = INTERNAL_EMAIL["host_user"]
EMAIL_HOST_PASSWORD = INTERNAL_EMAIL["host_password"]
EMAIL_BUG_LIST = INTERNAL_EMAIL["bug_list"]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{CACHE["host"]}:{CACHE["port"]}/{CACHE["db"]}',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y-%H:%M:%S"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG'
        },
        'graypy': {
            'level': 'DEBUG',
            'class': 'graypy.GELFUDPHandler',
            'host': LOG_CONFIG.get("gray_host", "10.10.4.51"),
            'port': LOG_CONFIG.get("gray_port", 5555),
            "facility": LOG_CONFIG.get("gray_facility", "poseidon")
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'api.log'),
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
        },
        'file_api_resp': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'resp_api.log'),
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
        }

    },
    'loggers': {
        '': {
            'handlers': LOG_CONFIG['main_log_handler'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),

        },
        'api_resp': {
            'handlers': LOG_CONFIG["api_resp_log_handler"],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False
        }
    },

}

