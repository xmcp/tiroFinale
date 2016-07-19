#coding=utf-8
import json

import requests
import cherrypy
import base64
import os

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

PORT=int(os.environ.get('PORT',4446))
CHUNKSIZE=64*1024
PASSWORD='rdfzyjy'
API_VERSION='APIv2'

class Website:
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    def finale(self,api='APIv1'):
        if api!=API_VERSION:
            cherrypy.response.status='400 Tiro Version Mismatch'
            cherrypy.response.headers['Content-Type']='text/plain'
            return 'Finale Error: You are running tiroFinale %s while this server is running %s.'%(api,API_VERSION)

        if cherrypy.request.json['auth']!=PASSWORD:
            cherrypy.response.status='401 Finale Password Incorrect'
            cherrypy.response.headers['Content-Type']='text/plain'
            return 'Finale Error: Your Password for tiroFinale is Incorrect'

        print('finale: %s %s'%(cherrypy.request.json['method'],cherrypy.request.json['url']))
        s=requests.Session()
        s.trust_env=False
        try:
            res=s.request(
                cherrypy.request.json['method'],
                cherrypy.request.json['url'],
                headers=cherrypy.request.json['headers'],
                data=base64.b64decode(cherrypy.request.json['data'].encode()),
                stream=True,
                allow_redirects=False,
                timeout=cherrypy.request.json['timeout'],
                verify=False,
            )
        except Exception as e:
            cherrypy.response.status='504 Finale Connection Failed'
            cherrypy.response.headers['Content-Type']='text/plain'
            return 'Finale Error: Request failed. %s %s'%(type(e),e)

        print('finale: [OK] %s'%cherrypy.request.json['url'])

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
    },
    '/finale': {
        'response.stream': True
    }
})

