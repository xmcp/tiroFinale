#coding=utf-8
import socketserver
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

import finale_launcher

HTTPS_PORT = 4443

class MultithreadServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url='https://%s%s'%(self.headers['Host'], self.path)
        body=self.rfile.read(self.headers.get('Content-Length',0)) #fixme: post request without content-length
        finale_launcher.base_fetcher(self,self.command,url,self.headers,body)

    do_POST=do_GET
    do_HEAD=do_GET
    do_DELETE=do_GET
    do_PATCH=do_GET
    do_PUT=do_GET

def run():
    httpsd = MultithreadServer(('127.0.0.1', HTTPS_PORT), MyHandler)
    httpsd.socket = ssl.wrap_socket(httpsd.socket, certfile='./key.pem', server_side=True)
    threading.Thread(target=httpsd.serve_forever).start()