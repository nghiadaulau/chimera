import logging
from datetime import time

import jwt
from django.conf import settings

from applications.commons.utils import datetime2timestamp

_logger = logging.getLogger("storage")


class AuthenticationToken(object):
    def __init__(self, user_id, expired_at):
        self.user_id = user_id
        self.expired_at = expired_at

    @property
    def token(self):
        """
        This function return token for user login
        :return:
        """
        payload = {
            "user_id": self.user_id,
            "expired_at": datetime2timestamp(self.expired_at)
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @classmethod
    def auth(cls, token):
        """
        Function use for check access-token is valid or not
        :param token:
        :return:
        """
        ins = None
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms="HS256")
            ins = cls(user_id=payload.get("user_id"), expired_at=payload.get("expired_at") - time.time())
        except Exception as e:
            _logger.error(e)
        return ins
