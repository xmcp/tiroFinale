#coding=utf-8

import requests
from contextlib import closing
import tornado.httputil
import base64

CHUNKSIZE = 64*1024
FINALE_URL = 'http://127.0.0.1:4446/finale'
TIMEOUT = 10
PASSWORD = 'rdfzyjy'

def _finale_request(method, url, headers, body):
    print('tiro: %s %s'%(method,url))
    s=requests.Session()
    s.trust_env=False #disable original proxy
    return closing(s.post(
        FINALE_URL,
        json={
            'auth': PASSWORD,
            'method': method,
            'url': url,
            'headers': dict(headers),
            'data': base64.b64encode(body or b'').decode(),
            'timeout': TIMEOUT
        },
        stream=True,allow_redirects=False,timeout=TIMEOUT
    ))

def tornado_fetcher(responder, method, url, headers, body):
    try:
        with _finale_request(method,url,headers,body) as res:
            responder.set_status(res.status_code, res.reason)
            responder._headers = tornado.httputil.HTTPHeaders()
            for k,v in res.headers.items():
                if k.lower() not in ['connection','transfer-encoding']:
                    responder.add_header(k, v)
            for content in res.raw.stream(CHUNKSIZE,decode_content=False):
                responder.write(content)
            responder.finish()
    except Exception as e:
        responder.set_status(504,'tiroFinale Error')
        responder.add_header('Content-Type','Text/Plain')
        responder.write('Exception occured in tiroFinale worker: %s %s'%(type(e),e))
        responder.finish()
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
        responder.wfile.write(('Exception occured in tiroFinale worker: %s %s'%(type(e),e)).encode('utf-8'))
        responder.wfile.close()
        raise