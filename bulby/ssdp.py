'''
Module for discovering services over SSDP (Simple Service Discovery Protocol)

Example usage:
from bulby import ssdp
ssdp.discover("IpBridge")
'''
import socket
import http
from io import BytesIO


class SSDPResponse(object):
    class _FakeSocket(BytesIO):
        def makefile(self, *args, **kw):
            return self

    def __init__(self, response):
        r = http.client.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader('location')
        self.usn = r.getheader('usn')
        self.st = r.getheader('st')
        self.cache = r.getheader('cache-control').split('=')[1]

    def __repr__(self):  # pragma: nocover
        return "<SSDPResponse({location}, {st}, {usn})>".format(
            **self.__dict__
        )


def discover(service, timeout=5, retries=5):
    '''
    Discovers services on a network using the SSDP Protocol.
    '''
    group = ('239.255.255.250', 1900)
    message = '\r\n'.join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}', 'MX: 3', '', ''])
    socket.setdefaulttimeout(timeout)
    responses = {}

    for _ in range(retries):
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        data = message.format(*group, st=service)
        sock.sendto(data.encode('utf-8'), group)

        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                responses[response.location] = response
            except socket.timeout:
                break

        if responses:
            break

    return responses.values()
