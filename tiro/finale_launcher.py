#coding=utf-8

import requests
import requests.exceptions
import urllib.parse
from contextlib import closing
from functools import lru_cache
import base64
import zlib
import json
import traceback

from portal import web_portal
import const
from utils import normdomain, load_gfwlist

API_VERSION = 'APIv5'
PORTAL_ROOT='http://127.0.0.1:%d' % const.PORTAL_PORT

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

gfwlist=load_gfwlist()
filtered_domains=set()
s=requests.Session()
s.trust_env=False #disable original proxy
s.proxies = const.PROXY_OVER_PROXIES or {}

thread_adapter=requests.adapters.HTTPAdapter(pool_connections=const.POOLSIZE, pool_maxsize=const.POOLSIZE)
s.mount('http://',thread_adapter)
s.mount('https://',thread_adapter)

def _real_finale_request(method, url, headers, body):
    print('tiro->Finale: %s %s'%(method,url))
    data={
        'auth': const.PASSWORD,
        'method': method,
        'url': url,
        'headers': dict(headers),
        'data': base64.b64encode(body or b'').decode(),
        'reuse': const.REUSE_SESSION,
        'timeout': const.TIMEOUT
    }
    dumped=json.dumps(data)
    res=s.post(
        const.FINALE_URL,
        params={'api':API_VERSION},
        json=[True,base64.b85encode(zlib.compress(dumped.encode())).decode()]\
            if const.COMPRESS_THRESHOLD and len(dumped) >= const.COMPRESS_THRESHOLD else [False, data],
        timeout=(const.TIMEOUT, const.FIRST_BYTE_TIMEOUT),
        stream=True, allow_redirects=False, verify=False,
    )

    if 'X-Finale-Status' in res.headers:
        res.status_code=int(res.headers['X-Finale-Status'])
        res.reason=res.headers['X-Finale-Reason']
        res.headers=json.loads(res.headers['X-Finale-Headers'])
    else:
        print('tiro: Finale error %d %s: %s'%(res.status_code,res.reason,url))
        return closing(requests.post(PORTAL_ROOT+'/error',stream=True,data={
            'level': 3,
            'reason': 'Finale server returns HTTP %d %s.'%(res.status_code,res.reason),
            'traceback': b''.join(res.iter_content()).decode('utf-8','ignore')
        }))

    print('tiro: [%d] %s'%(res.status_code,url))
    return closing(res)

def _direct_request(method, url, headers, body):
    print('tiro->Direct: %s %s'%(method,url))

    if const.REUSE_SESSION:
        ss=s
    else:
        ss=requests.Session()
        ss.trust_env=False
        ss.proxies = const.PROXY_OVER_PROXIES or {}
    try:
        res=ss.request(
            method, url,
            headers=headers, data=body,
            timeout=(const.TIMEOUT, const.FIRST_BYTE_TIMEOUT),
            stream=True, allow_redirects=False, verify=False,
        )
    except requests.exceptions.ConnectionError:
        if const.PROXY_MODE==1:
            domain=urllib.parse.urlsplit(url).netloc
            print('tiro->Rikka: Jao Shingan launched: %s'%domain)
            filtered_domains.add(normdomain(domain))
            _should_go_direct.cache_clear()
            return _real_finale_request(method, url, headers, body)
        raise

    print('tiro: [%d] %s'%(res.status_code,url))
    return closing(res)

@lru_cache()
def _should_go_direct(url):
    if url.partition('?')[0]==const.TEST_URL:
        return True
    else:
        domain=urllib.parse.urlsplit(url).netloc
        if const.PROXY_MODE==0 or domain.partition(':')[0]=='127.0.0.1':
            return True
        elif const.PROXY_MODE==1:
            return normdomain(domain) not in filtered_domains and not gfwlist(url)
        else:
            return False

def finale_request(method, url, headers, body):
    if url.partition('?')[0]==const.TEST_URL:
        return _direct_request('get',PORTAL_ROOT+'/intro?sub=1',{},None)
    elif _should_go_direct(url):
        return _direct_request(method, url, headers, body)
    else:
        return _real_finale_request(method, url, headers, body)

def tornado_fetcher(ioloop, puthead, putdata, finish, method, url, headers, body):
    try:
        with finale_request(method, url, headers, body) as res:
            ioloop.add_callback(puthead,res.status_code,res.reason,res.headers.items())
            for content in res.raw.stream(const.CHUNKSIZE, decode_content=False):
                ioloop.add_callback(putdata,content)
            ioloop.add_callback(finish)
    except:
        ioloop.add_callback(puthead,504,'tiroFinale Error',[('Content-Type','text/html')])
        ioloop.add_callback(putdata,web_portal.template('error.html').render(
            level=3 if _should_go_direct(url) else 2,
            reason='Exception occured in tiroFinale tornado wrapper.',
            traceback=traceback.format_exc(),
            direct=_should_go_direct(url),
        ))
        ioloop.add_callback(finish)
        raise

def base_fetcher(responder, method, url, headers, body):
    try:
        with finale_request(method, url, headers, body) as res:
            responder.send_response(res.status_code, res.reason)
            for k,v in res.headers.items():
                if k=='Set-Cookie':
                    for item in v.split(','):
                        responder.send_header('Set-Cookie',item)
                elif k not in ['Connection','Transfer-Encoding']:
                    responder.send_header(k, v)
            responder.end_headers()
            for content in res.raw.stream(const.CHUNKSIZE, decode_content=False):
                responder.wfile.write(content)
    except:
        responder.send_response(504,'tiroFinale Error')
        responder.send_header('Content-Type','text/html')
        responder.end_headers()
        responder.wfile.write(web_portal.template('error.html').render(
            level=3 if _should_go_direct(url) else 2,
            reason='Exception occured in tiroFinale HTTPS wrapper.',
            traceback=traceback.format_exc(),
            direct=_should_go_direct(url),
        ))
