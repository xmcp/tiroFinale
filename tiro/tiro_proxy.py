#coding=utf-8
#based on https://github.com/senko/tornado-proxy

import socket
import threading

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient
import tornado.httputil

import https_wrapper
import finale_launcher

PORT = 888

class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'HEAD', 'DELETE', 'PATCH', 'PUT', 'CONNECT']

    def compute_etag(self):
        return None # disable tornado Etag

    @tornado.web.asynchronous
    def get(self):
        def handle_response(response):
            if (response.error and not
                    isinstance(response.error, tornado.httpclient.HTTPError)):
                self.set_status(500)
                self.write('Internal server error:\n' + str(response.error))
            else:
                self.set_status(response.code, response.reason)
                self._headers = tornado.httputil.HTTPHeaders() # clear tornado default header

                for header, v in response.headers.get_all():
                    if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                        self.add_header(header, v) # some header appear multiple times, eg 'Set-Cookie'

                if response.body:
                    self.set_header('Content-Length', len(response.body))
                    self.write(response.body)
            self.finish()

        body = self.request.body
        try:
            if 'Proxy-Connection' in self.request.headers:
                del self.request.headers['Proxy-Connection']
            finale_launcher.tornado_fetcher(
                self,
                self.request.method,
                self.request.uri,
                self.request.headers,
                body,
            )
        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write('Internal server error:\n' + str(e))
                self.finish()

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
    app.listen(PORT)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()

if __name__ == '__main__':
    print("Starting HTTP proxy on port %d" % PORT)
    run_proxy()
