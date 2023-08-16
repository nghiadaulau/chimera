import datetime
import sys
import uuid
import logging
from django.conf import settings
from rest_framework import request, status
from rest_framework.response import Response

from applications.commons.exception import APIBreakException


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
        :param username: this username will be shown in each log line.
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

    def log(self, lv, message, func_name="", ):
        """
        :param lv: level to log
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        log_message = {
            'func_name': self.func_name if not func_name else func_name,
            'message': message,
            'user': self.user,
            "traceback": "trace-id-{}".format(self.trace_id),
            "time": f"{datetime.datetime.now()}"
        }

        my_adapter = logging.LoggerAdapter(self._logger,
                                           {
                                               'func_name': self.func_name if not func_name else func_name,
                                               'user': self.user,
                                               "traceback": "trace-id-{}".format(self.trace_id),
                                               "time": f"{datetime.datetime.now()}"
                                           })

        # print(log_message)
        self.logs_message(lv, log_message, my_adapter)

    def info(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.log("info", message, func_name)

    def error(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.log("error", message, func_name)

    def warning(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.log("warning", message, func_name)

    def debug(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        if settings.LOG_DEBUG:
            self.log("info", message, func_name)

    @classmethod
    def init_log(cls, func_name, logger=None, user="", client_id="", service_name=""):
        """
        :param func_name: function name where we wrote log line
        :param logger: logger object or logger name.
        :param user: username to log
        :param client_id: client_id to identify who call api
        :param service_name: service name to identify what service logged
        :return:
        """
        if not logger:
            init_service_name = service_name if service_name else settings.SERVICE_NAME
            log_message = cls(func_name=func_name, user=user, service_name=init_service_name)
        elif isinstance(logger, cls):
            user = logger.user
            init_service_name = service_name if service_name else logger.service_name
            log_message = cls(func_name=func_name, logger=logger.pub_logger, user=user, client_id=logger.client_id,
                              trace_id=logger.trace_id, service_name=init_service_name)
        elif isinstance(logger, MixingLog):
            user = logger.default.user
            init_service_name = service_name if service_name else logger.default.service_name
            log_message = cls(func_name=func_name, logger=logger.default.pub_logger, user=user,
                              client_id=logger.client_id, trace_id=logger.default.trace_id,
                              service_name=init_service_name)
        else:
            init_service_name = service_name if service_name else settings.SERVICE_NAME
            log_message = cls(func_name=func_name, logger=logger, user=user, client_id=client_id,
                              service_name=init_service_name)
        return log_message


class MixingLog(object):
    def __init__(self, func_name="", user=None, init_span=True, _parent_logger=None, client_id="", service_name=None):
        self.func_name = func_name
        self.user = user
        self.default = None
        self.client_id = client_id
        self._parent_logger = _parent_logger
        self.span = None
        self.init_span = init_span
        self.service_name = service_name if service_name else settings.SERVICE_NAME
        self.init_log_base_settings()

    @property
    def trace_id(self):
        """
        This function to show trace id of logger into log line.
        :return:
        """
        return self.default.trace_id if self.default else uuid.uuid1().hex

    def set_user_log(self, username):
        """
        This func to set user into logger.
        :param username: this username will be shown in each log line.
        :return:
        """
        self.user = username
        if self.default:
            self.default.set_user_log(username)

    def init_log_base_settings(self):
        """
        This func to set init for log base setting.
        :return:
        """
        if self.init_span:
            if isinstance(self._parent_logger, (LogMessage, MixingLog)):
                self.user = self._parent_logger.user
                self.client_id = self._parent_logger.client_id
        self.default = LogMessage(logger="", func_name=self.func_name, client_id=self.client_id, user=self.user,
                                  service_name=self.service_name)
        self.span = self.default.span
        for i in settings.LOGGING["loggers"].keys():
            if i:
                setattr(self, i,
                        LogMessage(logger=i, func_name=self.func_name, user=self.user, client_id=self.client_id,
                                   service_name=self.service_name))

    def set_component(self, value):
        """
        This function to set up component value.
        :param value:
        :return:
        """
        return self.default.set_component(value)

    def info(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.default.info(message, func_name)

    def error(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.default.error(message, func_name)

    def warning(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.default.warning(message, func_name)

    def log(self, lv, message, func_name=""):
        """
        :param lv: This is a level of log
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.default.log(lv, message, func_name)

    def debug(self, message, func_name=""):
        """
        :param message: message to log
        :param func_name: function name where we wrote log line
        :return:
        """
        self.default.debug(message, func_name)


class APIResponse(object):
    """
    This class to custom format response api
    """

    def __init__(self):
        self.status_code = 0
        self.message = ""
        self.errors = {}
        self.data = {}
        self.kwargs = {}
        self.trace = ""

    def check_message(self, message):
        """
        This function to check message with init
        :param message: Message of APIResponse
        :return:
        """
        self.message = self.message if self.message else message

    def check_status_code(self, status_code):
        """
        This function to check http code.
        :param status_code: status code of APIResponse
        :return:
        """
        self.status_code = self.status_code if self.status_code else status_code

    def create_errors(self, errors):
        """
        This function to create errors into APIResponse
        :param errors: that is errors
        :return:
        """
        if isinstance(errors, list):
            self.errors.update(errors)
        else:
            self.errors.update(errors)

    def get_status_code(self, code=200):
        """
        This function to get http status code
        :param code: A status of http request
        :return: http status code
        """
        return self.status_code if self.status_code else code

    def make_format(self):
        """
        This function to format response of api for commons structure
        :return: Format of APIResponse
        """
        if self.errors:
            status_code = self.get_status_code(400)
            message = self.message
            result = False
        else:
            status_code = self.get_status_code(200)
            message = self.message if self.message else 'Success'
            result = True
        return dict(result=result, message=str(message), status_code=status_code, request_id=str(self.trace),
                    data=self.data, error=self.errors, **self.kwargs)


def trace_api(specific_logger="", serializer=None, service_name=None, check_content_type=None,
              class_response=APIResponse):
    """
    This function to trace log of api
    :param check_content_type: Check content type for trace api
    :param serializer: Serializer for api
    :param specific_logger: Logger specific for api
    :param service_name: Service name for log
    :param class_response: Response class to
    :return:
    """

    def decorator(func):
        """
        :param func: api function using this decorator
        :return: inner func
        """

        def inner(request, **kwargs):
            """
            :param request: request http
            :param kwargs: key word arguments
            :return: json payload to response to client
            """
            _response = class_response()
            kwargs.update(_response=_response)
            func_name = f"{func.__name__}"
            if specific_logger == "":
                _logger = LogMessage.init_log(func_name, service_name=service_name)
            elif specific_logger == "mix":
                _logger = MixingLog(func_name=func_name, service_name=service_name)
            else:
                _logger = LogMessage.init_log(func_name, service_name=service_name)
            kwargs.update(request=request, data_ser=None, logger=_logger)
            _response.trace = _logger.trace_id
            _logger.debug("<-------START------->")
            _logger.debug(f'Input request {request.data}')
            _logger.debug(f'Input params {request.query_params}')
            if check_content_type and 'x-www-form-urlencoded' not in request.content_type and 'form-data' not in request.content_type and 'application/json' not in request.content_type:
                _response.check_message('Content-type has incorrect format')
                _response.create_errors({
                    "header": {
                        "message": "Content-type has incorrect format"
                    }
                })
                _response.check_status_code(406)
                _logger.warning("<-------END------->")
                return Response(_response.make_format(), status=status.HTTP_200_OK)
            kwargs.update(request=request, data_ser=None, logger=_logger)
            if serializer:
                _logger.info(f'Input params {request.data}')
                data_ser = serializer(data=request.data)
                if not data_ser.is_valid():
                    _response.check_message('Data input is invalid.')
                    _response.check_status_code(400)
                    ctx = []
                    for key_error in data_ser.errors.keys():
                        if isinstance(data_ser.errors[key_error], dict):
                            for key_errors in data_ser.errors[key_error]:
                                ctx.append({
                                    'field': '{}.{}'.format(key_error, key_errors),
                                    'message': data_ser.errors[key_error][key_errors][0]
                                })
                        else:
                            ctx.append({
                                'field': key_error,
                                'message': data_ser.errors[key_error][0]
                            })
                    _response.create_errors({
                        "serializer": {
                            "errors": ctx
                        }
                    })

                    _logger.info('Error: {}'.format(ctx))
                    return Response(_response.make_format(), status=status.HTTP_200_OK)
                kwargs.update(data_ser=data_ser.data)

            try:
                func(**kwargs)
            except Exception as e:
                if not isinstance(e, APIBreakException):
                    _response.check_message('Ops! Something were wrong.')
                    _response.check_status_code(1400)
                    _response.create_errors({"unknown_error": {
                        'field': "",
                        'message': 'An error occurred. Please try again later.' if not _response.message else _response.message
                    }})
                    log_traceback(trac_back=sys.exc_info()[-1], _logger=_logger, e=e, log_type="warning")
                else:
                    log_traceback(trac_back=sys.exc_info()[-1], _logger=_logger, e=e)
            if _response.errors:
                _logger.warning("<-------END------->")
            else:
                _logger.debug("<-------END------->")
            return Response(_response.make_format(), status=status.HTTP_200_OK)

        inner.func_name = func.__name__
        inner.__name__ = func.__name__
        return inner

    return decorator


def log_traceback(trac_back, e, _logger, log_type="info"):
    _logger.log(log_type, "{} - {}".format(e.__class__.__name__, str(e)))
    for i in range(8):
        if not i:
            continue
        if not trac_back:
            break
        if log_type == "info":
            _logger.log(log_type,
                        'Trace back exception at func {} - in line {}'.format(trac_back.tb_frame.f_code.co_name,
                                                                              trac_back.tb_lineno))
        else:
            _logger.log(log_type,
                        'Trace back exception at func {} - in line {}'.format(trac_back.tb_frame.f_code.co_name,
                                                                              trac_back.tb_lineno))
        trac_back = trac_back.tb_next
