import json
import uuid
import requests
from django.conf import settings

from applications.commons.log_lib import trace_func
from applications.commons.request_basic import RequestFetch


class SearchEngine(object):
    def __init__(self, protocol, host, port, username=None, password=None, **kwargs):
        self.protocol = protocol
        self.host_name = host
        self.port = port
        self.username = username
        self.password = password
        self.url = self.get_url()
        self.get_success = True
        self.error_data = []
        self.client = self.get_client()

    def get_client(self, logger=None):
        return requests.get(self.url)

    @staticmethod
    def get_url():
        if settings.SEARCH_ENGINE.get("username") and settings.SEARCH_ENGINE.get("password"):
            url = f'{settings.SEARCH_ENGINE["protocol"]}://{settings.SEARCH_ENGINE["username"]}:{settings.SEARCH_ENGINE["password"]}@{settings.SEARCH_ENGINE["host"]}:{settings.SEARCH_ENGINE.get("port", 80)}'
        else:
            url = f'{settings.SEARCH_ENGINE["protocol"]}://{settings.SEARCH_ENGINE["host"]}:{settings.SEARCH_ENGINE.get("port", 80)}'
        return url

    @trace_func()
    def put_data(self, index_name, body, _id=None, timeout=10, logger=None):
        _id = uuid.uuid1().hex if not _id else _id
        url = f"{self.client}/{index_name}/_doc/{_id}"
        resp = {
            "result": False,
            "data": {}
        }
        response = self.client
        response = requests.post(url=url, verify=False, json=body, timeout=timeout)
        try:
            logger.info(f'Put event meta to SearchEngine - body {body} with result {response.json()["result"]}')
            resp["result"] = True
            resp["data"] = {
                "resp": response.json()["result"],
                "id": _id
            }

        except Exception as e:
            logger.error(f'Put meta to SearchEngine Failed - body {body} with result {response.text} and error {e}')
        print(resp)
        return resp

    @trace_func()
    def search_data(self, index_name, body, timeout=10, logger=None):
        url = f"{self.url}/{index_name}/_search?ignore_unavailable=true"
        data = {}
        self.get_success = True
        try:
            response = requests.get(url=url, verify=False, json=body, timeout=timeout)
            logger.debug('Get data in SearchEngine - index {} - filter {} with shard data {}'.format(index_name,
                                                                                                     json.dumps(body),
                                                                                                     response.text))
            if settings.DEBUG:
                logger.debug('Log body SearchEngine - {}'.format(json.dumps(body)))
            data = response.json()
            if settings.DEBUG:
                logger.debug('Log response SearchEngine - {}'.format(data))
        except Exception as e:
            self.get_success = False
            self.error_data.append(str(e))
            logger.error('Get data in SearchEngine - index {} - filter {} with shard data {}'.format(index_name,
                                                                                                     json.dumps(body),
                                                                                                     str(e)))
        return data

    @trace_func()
    def remove_index(self, index_name, timeout=10, logger=None):
        url = f"{self.url}/{index_name}?ignore_unavailable=true"
        data = None
        self.get_success = True
        try:
            response = requests.delete(url=url, verify=False, timeout=timeout)
            if response.json()["acknowledged"]:
                logger.debug('Remove index {} successful'.format(index_name))
        except Exception as e:
            self.get_success = False
            self.error_data.append(str(e))
            logger.error('Error remove index {} with error {}'.format(index_name, str(e)))
        return data
