#coding=utf-8

import cherrypy
from mako.lookup import TemplateLookup
import os

from const import PORTAL_PORT, _PORTAL_CALLBACK

_lookup=TemplateLookup('portal/templates',input_encoding='utf-8',output_encoding='utf-8')
def template(name):
    return _lookup.get_template(name)

class WebPortal:
    @cherrypy.expose()
    def intro(self,sub=False):
        if sub:
            if sub=='real':
                return '<script>top.%s();</script>'%_PORTAL_CALLBACK
            else:
                raise cherrypy.HTTPRedirect('/intro?sub=real')
        else:
            return template('intro.html').render()

    @cherrypy.expose()
    def index(self):
        return template('index.html').render()

    @cherrypy.expose()
    def error(self,level,reason,traceback):
        cherrypy.response.status='504 Tiro Portal Error Page'
        return template('error.html').render(level=int(level),reason=reason,traceback=traceback,direct=False)

    @cherrypy.expose()
    def conf(self):
        pass #todo

conf={
    'global': {
        'engine.autoreload.on':False,
        'environment':'production',
        'server.socket_host':'127.0.0.1',
        'server.socket_port':PORTAL_PORT,
        'server.thread_pool':10,
    },
    '/': {
        'tools.gzip.on': True,
    },
    '/static': {
        'tools.staticdir.on':True,
        'tools.staticdir.dir':os.path.join(os.getcwd(),'portal/static'),
    },
}

def run():
    cherrypy.quickstart(WebPortal(),'/',conf)
if __name__=='__main__':
    run()