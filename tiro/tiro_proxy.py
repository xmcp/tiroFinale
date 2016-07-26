#coding=utf-8
#based on https://github.com/senko/tornado-proxy

import socket
import threading
import webbrowser

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient
import tornado.httputil

import https_wrapper
import finale_launcher
from portal import web_portal

from const import PROXY_PORT, PORTAL_PORT


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'HEAD', 'DELETE', 'PATCH', 'PUT', 'CONNECT']

    def compute_etag(self):
        return None # disable tornado Etag

    @tornado.web.asynchronous
    def get(self):
        def callback_puthead(code,reason,headers):
            self.set_status(code, reason)
            self._headers = tornado.httputil.HTTPHeaders()
            for k,v in headers:
                if k.lower() not in ['connection','transfer-encoding']:
                    self.add_header(k, v)
            self.flush()
        
        def callback_putdata(data):
            self.write(data)
            self.flush()
        
        def callback_finish():
            self.finish()
            
        body = self.request.body
        if 'Proxy-Connection' in self.request.headers:
            del self.request.headers['Proxy-Connection']

        finale_launcher.tornado_fetcher(
            ioloop,
            callback_puthead,
            callback_putdata,
            callback_finish,
            self.request.method,
            self.request.uri,
            self.request.headers,
            body,
        )

    post=get
    head=get
    delete=get
    patch=get
    put=get

    @tornado.web.asynchronous
    def connect(self):
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            client.read_until_close(client_close, upstream.write)
            upstream.read_until_close(upstream_close, client.write)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)

        upstream.connect(('127.0.0.1', https_wrapper.create_wrapper(host)), start_tunnel)
         
def run_proxy():
    app = tornado.web.Application([
        (r'.*', ProxyHandler),
    ])
    app.listen(PROXY_PORT)
    global ioloop
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()

if __name__ == '__main__':
    print('portal: starting web portal on port %d'%PORTAL_PORT)
    threading.Thread(target=web_portal.run).start()
    print('main: starting HTTP proxy on port %d'%PROXY_PORT)
    webbrowser.open('http://127.0.0.1:%d/intro'%PORTAL_PORT)
    run_proxy()