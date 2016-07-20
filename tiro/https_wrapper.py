#coding=utf-8
import socketserver
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os

import finale_launcher
from makecert import CertManager
import ssl_config
from const import SSL_WILDCARD

class MultithreadServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url='https://%s%s'%(self.headers['Host'], self.path)
        body=self.rfile.read(int(self.headers.get('Content-Length',0))) #fixme: post request without content-length
        finale_launcher.base_fetcher(self,self.command,url,self.headers,body)

    do_POST=do_GET
    do_HEAD=do_GET
    do_DELETE=do_GET
    do_PATCH=do_GET
    do_PUT=do_GET
    
    def log_message(self,*_):
        pass #default server log

_psl=None
def normdomain(domain):
    from publicsuffix import PublicSuffixList
    global _psl

    if _psl is None:
        print('ssl: loading public suffix list')
        _psl=PublicSuffixList(open(ssl_config.psl_filename, encoding='utf-8'))

    suf=_psl.get_public_suffix(domain)
    return domain if domain==suf else '*.%s'%suf

cache={}
def create_wrapper(host):
    if SSL_WILDCARD:
        host=normdomain(host)
    if host in cache:
        return cache[host]

    ssl_check, fdomain = CertManager().generate(host)
    httpsd = MultithreadServer(('127.0.0.1', 0), MyHandler)

    if not ssl_check:
        print('https_wrapper: gen cert failed. using CA instead.')
        httpsd.socket=ssl.wrap_socket(httpsd.socket,certfile=ssl_config.ca_pem_file,server_side=True)
    else:
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        sslcontext.load_cert_chain(
            os.path.join(ssl_config.key_dir,fdomain+'.crt'),
            keyfile=os.path.join(ssl_config.key_dir,fdomain+'.key')
        )
        httpsd.socket=sslcontext.wrap_socket(httpsd.socket,server_side=True)

    httpsd.handle_error=lambda *_: None #suppress annoying "ValueError: I/O operation on closed file"
    port = httpsd.socket.getsockname()[1]
    threading.Thread(target=httpsd.serve_forever).start()

    print('https_wrapper: wrapping %s on port %d'%(host,port))
    cache[host]=port
    return port

if __name__=='__main__':
    create_wrapper('www.t.cn')