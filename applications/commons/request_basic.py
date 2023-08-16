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


