#coding=utf-8
#based on https://github.com/senko/tornado-proxy

print('bootstrap: loading third-party libraries')

import socket
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor

import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.gen
import tornado.httputil
from tornado.concurrent import run_on_executor

print('bootstrap: loading components')

import https_wrapper
import finale_launcher
from portal import web_portal

from const import PROXY_PORT, PORTAL_PORT, POOLSIZE, SHOW_INTRO, MAX_REQ_BODY
from utils import set_proxy, install_ca


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'HEAD', 'DELETE', 'PATCH', 'PUT', 'OPTIONS', 'CONNECT']
    executor=ThreadPoolExecutor(POOLSIZE)

    def compute_etag(self):
        return None # disable tornado Etag

    def _async(self,fn,*args,**kwargs):
        def self_remover(_,*args,**kwargs):
            return fn(*args,**kwargs)
        return run_on_executor(executor='executor')(self_remover)(self,*args,**kwargs)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        def callback_puthead(code,reason,headers):
            self.set_status(code, reason)
            self._headers = tornado.httputil.HTTPHeaders()
            for k,v in headers:
                if k=='Set-Cookie':
                    for item in v.split(','):
                        self.add_header('Set-Cookie',item)
                elif k not in ['Connection','Transfer-Encoding']:
                    self.add_header(k, v)
            self.flush()

        body = self.request.body
        if 'Proxy-Connection' in self.request.headers:
            del self.request.headers['Proxy-Connection']

        yield self._async(finale_launcher.tornado_fetcher,
            ioloop,
            callback_puthead, self.write, self.finish,
            self.request.method, self.request.uri, self.request.headers, body,
        )

    post=get
    head=get
    delete=get
    patch=get
    put=get
    options=get

    @tornado.web.asynchronous
    def connect(self):
        host=self.request.uri.partition(':')[0]
        client=self.request.connection.stream

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

        s = socket.socket()
        upstream = tornado.iostream.IOStream(s)

        upstream.connect(('127.0.0.1', https_wrapper.create_wrapper(host)), start_tunnel)
         
def run_proxy():
    tornado.web.Application([
        (r'.*', ProxyHandler),
    ]).listen(PROXY_PORT,max_body_size=MAX_REQ_BODY)
    global ioloop
    ioloop = tornado.ioloop.IOLoop.instance()
    print('='*30,' tiro started up ','='*30)
    ioloop.start()

if __name__ == '__main__':

    print('bootstrap: starting web portal on port %d'%PORTAL_PORT)
    threading.Thread(target=web_portal.run).start()

    print('bootstrap: setting-up environment')
    install_ca()
    set_proxy()
    if SHOW_INTRO and not webbrowser.open('http://127.0.0.1:%d/intro'%PORTAL_PORT):
        print('bootstrap: please visit http://127.0.0.1:%d/intro'%PORTAL_PORT)

    print('bootstrap: starting HTTP proxy on port %d'%PROXY_PORT)
    run_proxy()