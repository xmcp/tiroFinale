#coding=utf-8
import json
import traceback
import requests
import cherrypy
import base64
import zlib
import os

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

PORT=int(os.environ.get('PORT',4446))
CHUNKSIZE=64*1024
PASSWORD='rdfzyjy'
API_VERSION='APIv5'
POOLSIZE=100
FIRST_BYTE_TIMEOUT=300

class Website:
    def __init__(self):
        self.session=requests.Session()
        self.session.trust_env=False
        thread_adapter=requests.adapters.HTTPAdapter(pool_connections=POOLSIZE, pool_maxsize=POOLSIZE)
        self.session.mount('http://',thread_adapter)
        self.session.mount('https://',thread_adapter)

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    def finale(self,api='UNDEFINED_VERSION'):
        if api!=API_VERSION:
            cherrypy.response.status='400 tiroFinale Version Mismatch'
            cherrypy.response.headers['Content-Type']='text/plain'
            return 'You are running tiroFinale client %s while this server runs %s. ' \
                   'Visit https://github.com/xmcp/tiroFinale to update your client.'%(api,API_VERSION)

        data=cherrypy.request.json[1]
        if cherrypy.request.json[0]: #compression flag
            try:
                data=json.loads(zlib.decompress(base64.b85decode(data.encode())).decode())
            except Exception as e:
                cherrypy.response.status='500 Finale Decoding Error'
                cherrypy.response.headers['Content-Type']='text/plain'
                return "Finale Error: Cannot decode client's compressed data. %s %s"%(type(e),e)

        if data['auth']!=PASSWORD:
            cherrypy.response.status='401 Finale Password Incorrect'
            cherrypy.response.headers['Content-Type']='text/plain'
            return 'Finale Error: Your password for tiroFinale is incorrect.'

        print('finale: %s %s'%(data['method'],data['url']))
        if data['reuse']:
            s=self.session
        else:
            s=requests.Session()
            s.trust_env=False
        try:
            res=s.request(
                data['method'],
                data['url'],
                headers=data['headers'],
                data=base64.b64decode(data['data'].encode()),
                stream=True,
                allow_redirects=False,
                timeout=(data['timeout'],FIRST_BYTE_TIMEOUT),
                verify=False,
            )
        except:
            cherrypy.response.status='504 Finale Connection Failed'
            cherrypy.response.headers['Content-Type']='text/plain'
            return traceback.format_exc()

        print('finale: [%d] %s'%(res.status_code,data['url']))

        def extract():
            yield from res.raw.stream(CHUNKSIZE,decode_content=False)
        def addheader(k):
            if k in res.headers:
                cherrypy.response.headers[k]=res.headers[k]

        cherrypy.response.status='200 Finale Itself OK'
        addheader('Content-Length')
        addheader('Content-Encoding')
        cherrypy.response.headers['X-Finale-Status']=res.status_code
        cherrypy.response.headers['X-Finale-Reason']=res.reason
        cherrypy.response.headers['X-Finale-Headers']=json.dumps(dict(res.headers))
        return extract()

cherrypy.quickstart(Website(),'/',{
    'global': {
        'environment': 'production',
        'server.socket_host':'0.0.0.0',
        'server.socket_port':PORT,
        'tools.response_headers.on':True,
        'engine.autoreload.on':False,
        'server.thread_pool': 25,
        'server.max_request_body_size': 0, #no limit
        'response.timeout': 900,
    },
    '/finale': {
        'response.stream': True
    }
})

