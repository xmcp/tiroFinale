#coding=utf-8

import requests
import cherrypy
import base64
import os

PORT=int(os.environ.get('PORT',4446))
CHUNKSIZE=64*1024
PASSWORD='rdfzyjy'

class Website:
    @cherrypy.expose()
    @cherrypy.tools.json_in()
    def finale(self):
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

        #todo: store all data in response body
        cherrypy.response.status='%d %s'%(res.status_code,res.reason)
        for k,v in res.headers.items():
            cherrypy.response.headers[k]=v
        return extract()

cherrypy.quickstart(Website(),'/',{
    'global': {
        'server.socket_host':'0.0.0.0',
        'server.socket_port':PORT,
        'tools.response_headers.on':True,
        'engine.autoreload.on':False,
        # 'request.show_tracebacks': False,
    },
    '/finale': {
        'response.stream': True
    }
})

