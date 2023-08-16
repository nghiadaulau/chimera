import uuid
import logging

from django.conf import settings


class LogMessage(object):
    """
    This class is used to manage LogMessage.
    """

    def __init__(self, logger=None, func_name="", user="", client_id="", trace_id=None, service_name=None):
        self._logger = self.get_logger(logger)
        self.func_name = func_name
        self.user = user
        self.client_id = client_id
        self.tracer = None
        self.span = None
        self.trace_id = uuid.uuid1().hex if not trace_id else trace_id
        self.service_name = service_name if service_name else settings.SERVICE_NAME

    @staticmethod
    def get_logger(logger=None):
        """
        This function to get logger init
        :param logger: logger_name
        :return: logger object
        """
        if isinstance(logger, (logging.Logger, logging.RootLogger)):
            return logger
        else:
            return logging.getLogger("" if not logger else logger)

    def set_user_log(self, username):
        """
        This func to set user into logger.
        :param username: this username will be show in each log line.
        :return:
        """
        self.user = username

    @property
    def pub_logger(self):
        """
        This function to get logger object.
        :return: logger object.
        """
        return self._logger

    @staticmethod
    def logs_message(level, message, logger_obj):
        """
        :param level: level to log
        :param message: message to log
        :param logger_obj: log adapter
        :return:logger line with level.
        """
        level = level.upper()
        logger_level = {
            'CRITICAL': 50,
            'ERROR': 40,
            'WARNING': 30,
            'INFO': 20,
            'DEBUG': 10,
            'NOTSET': 0
        }
        logger_obj.log(logger_level.get(level), message)
