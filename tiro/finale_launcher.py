#coding=utf-8

import requests
from contextlib import closing
import tornado.httputil
import base64

import threading
import json
import time
CHUNKSIZE = 64*1024
FINALE_URL = 'http://127.0.0.1:4446/finale'
TIMEOUT = 30
PASSWORD = 'rdfzyjy'
API_VERSION = 'APIv2'
POOLSIZE = 100

s=requests.Session()
s.trust_env=False #disable original proxy
thread_adapter=requests.adapters.HTTPAdapter(pool_connections=POOLSIZE, pool_maxsize=POOLSIZE)
s.mount('http://',thread_adapter)

def _finale_request(method, url, headers, body):
    print('tiro: %s %s'%(method,url))
    res=s.post(
        FINALE_URL,
        params={'api':API_VERSION},
        json={
            'auth': PASSWORD,
            'method': method,
            'url': url,
            'headers': dict(headers),
            'data': base64.b64encode(body or b'').decode(),
            'timeout': TIMEOUT
        },
        stream=True,allow_redirects=False,timeout=TIMEOUT
    )

    if 'X-Finale-Status' in res.headers:
        res.status_code=int(res.headers['X-Finale-Status'])
        res.reason=res.headers['X-Finale-Reason']
        res.headers=json.loads(res.headers['X-Finale-Headers'])
    else:
        print('tiro: Finale error %d %s: %s'%(res.status_code,res.reason,url))
        
    print('tiro: [%d] %s'%(res.status_code,url))
    return closing(res)

def _async(f):
    def _real(*__,**_):
        threading.Thread(target=f,args=__,kwargs=_).start()
    return _real

@_async
def tornado_fetcher(ioloop, puthead, putdata, finish, method, url, headers, body):
    try:
        with _finale_request(method,url,headers,body) as res:
            ioloop.add_callback(puthead,res.status_code,res.reason,res.headers.items())
            for content in res.raw.stream(CHUNKSIZE,decode_content=False):
                ioloop.add_callback(putdata,content) #fixme: "Tried to write more data than Content-Length"
            ioloop.add_callback(finish); print('<< DONE >>')
    except Exception as e:
        ioloop.add_callback(puthead,504,'tiroFinale Error',[('Content-Type','Text/Plain')])
        ioloop.add_callback(putdata,'Exception occured in tiroFinale tornado worker: %s %s'%(type(e),e))
        ioloop.add_callback(finish)
        raise

def base_fetcher(responder, method, url, headers, body):
    try:
        with _finale_request(method,url,headers,body) as res:
            responder.send_response(res.status_code, res.reason)
            for k,v in res.headers.items():
                if k not in ['Connection','Transfer-Encoding']:
                    responder.send_header(k, v)
            responder.end_headers()
            for content in res.raw.stream(CHUNKSIZE,decode_content=False):
                responder.wfile.write(content)
            responder.wfile.close()
    except Exception as e:
        responder.send_response(504,'tiroFinale Error')
        responder.send_header('Content-Type','Text/Plain')
        responder.end_headers()
        responder.wfile.write(('Exception occured in tiroFinale https worker: %s %s'%(type(e),e)).encode('utf-8'))
        responder.wfile.close()
        raise