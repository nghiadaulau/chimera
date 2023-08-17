from applications.commons.log_lib import trace_func
import requests


class RequestFetch(object):
    POST = "post"
    GET = "get"
    PUT = "put"
    DELETE = "delete"

    def __init__(self, protocol, host_name, service_name, header=None, gis=None, cert=False):
        self.service_name = service_name
        self.host_name = host_name
        self.gis = gis
        self.protocol = protocol
        self.cert = cert
        self.header = {} if not header else header
        self.url = "{}://{}".format(self.protocol, self.host_name)

    def get_header(self, header=None):
        default_header = {}
        if self.gis:
            default_header.update({
                "gis": self.gis
            })
        if header:
            default_header.update(header)
        return default_header

    @trace_func()
    def fetch(self, uri='', body=None, files=None, logger=None, header=None, method="post", timeout=10, params=None,
              log_resp=True, **kwargs):
        if uri.startswith("/"):
            full_url = "{}{}".format(self.url, uri) if uri else self.url
        else:
            full_url = "{}/{}".format(self.url, uri) if uri else self.url
        func_call = getattr(requests, method)
        header = self.get_header(header)
        func_name = uri.replace("/", "_").replace("-", "_")
        logger.debug("call {} with url {} body {}".format(func_name, full_url, body))
        data = {
            "result": False
        }
        body = body if body else {}
        try:
            response = func_call(full_url, json=body, headers=header, files=files, verify=self.cert, timeout=timeout,
                                 params=params if params else {})
            data.update(http_status=response.status_code)
        except Exception as e:
            logger.error(f"call {func_name} error with {e}")
        else:
            try:
                data.update({"data": response.json()})
                data["result"] = True
            except Exception as e:
                logger.error(f"parse data error with {response.content} and exception {e}")
            else:
                if log_resp:
                    logger.debug('Call API {} SUCCESS: {}'.format(func_name, data))

        return data
