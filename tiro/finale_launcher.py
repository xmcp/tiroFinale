#coding=utf-8

import requests
import urllib.parse
from contextlib import closing
from functools import lru_cache
import base64
import zlib
import threading
import json

import gfwlist
from const import CHUNKSIZE, FINALE_URL, TIMEOUT, PASSWORD, POOLSIZE, COMPRESS_THRESHOLD, GFWLIST_ENABLED, REUSE_SESSION
API_VERSION = 'APIv4'

s=requests.Session()
s.trust_env=False #disable original proxy
thread_adapter=requests.adapters.HTTPAdapter(pool_connections=POOLSIZE, pool_maxsize=POOLSIZE)
s.mount('http://',thread_adapter)
s.mount('https://',thread_adapter)

def _real_finale_request(method, url, headers, body):
    print('tiro->Finale: %s %s'%(method,url))
    data={
        'auth': PASSWORD,
        'method': method,
        'url': url,
        'headers': dict(headers),
        'data': base64.b64encode(body or b'').decode(),
        'reuse': REUSE_SESSION,
        'timeout': TIMEOUT
    }
    dumped=json.dumps(data)
    res=s.post(
        FINALE_URL,
        params={'api':API_VERSION},
        json=[True,base64.b85encode(zlib.compress(dumped.encode())).decode()]\
            if COMPRESS_THRESHOLD and len(dumped)>=COMPRESS_THRESHOLD else [False,data],
        stream=True, allow_redirects=False, timeout=TIMEOUT,
    )

    if 'X-Finale-Status' in res.headers:
        res.status_code=int(res.headers['X-Finale-Status'])
        res.reason=res.headers['X-Finale-Reason']
        res.headers=json.loads(res.headers['X-Finale-Headers'])
    else:
        print('tiro: Finale error %d %s: %s'%(res.status_code,res.reason,url))
        
    print('tiro: [%d] %s'%(res.status_code,url))
    return closing(res)

def _direct_request(method, url, headers, body):
    print('tiro->Direct: %s %s'%(method,url))

    if REUSE_SESSION:
        ss=s
    else:
        ss=requests.Session()
        ss.trust_env=False
    res=ss.request(
        method, url,
        headers=headers, data=body,
        stream=True, allow_redirects=False, timeout=TIMEOUT,
    )

    print('tiro: [%d] %s'%(res.status_code,url))
    return closing(res)

@lru_cache()
def _is_domain_filtered(domain):
    domain=domain.split('.')
    return any((True for x in range(len(domain)) if '.'.join(domain[x:]) in gfwlist.domains))

def finale_request(method, url, headers, body):
    if GFWLIST_ENABLED:
        domain=urllib.parse.urlsplit(url).netloc
        if _is_domain_filtered(domain):
            return _real_finale_request(method, url, headers, body)
        else:
            return _direct_request(method, url, headers, body)
    else:
        return _real_finale_request(method, url, headers, body)

def _async(f):
    def _real(*__,**_):
        threading.Thread(target=f,args=__,kwargs=_).start()
    return _real

@_async
def tornado_fetcher(ioloop, puthead, putdata, finish, method, url, headers, body):
    try:
        with finale_request(method, url, headers, body) as res:
            ioloop.add_callback(puthead,res.status_code,res.reason,res.headers.items())
            for content in res.raw.stream(CHUNKSIZE,decode_content=False):
                ioloop.add_callback(putdata,content) #fixme: "Tried to write more data than Content-Length"
            ioloop.add_callback(finish)
    except Exception as e:
        ioloop.add_callback(puthead,504,'tiroFinale Error',[('Content-Type','Text/Plain')])
        ioloop.add_callback(putdata,'Exception occured in tiroFinale tornado worker: %s %s'%(type(e),e))
        ioloop.add_callback(finish)
        raise

def base_fetcher(responder, method, url, headers, body):
    try:
        with finale_request(method, url, headers, body) as res:
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