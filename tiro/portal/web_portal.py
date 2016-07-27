#coding=utf-8

import cherrypy
from mako.lookup import TemplateLookup
import os

from finale_launcher import _should_go_direct
import const

_lookup=TemplateLookup('portal/templates',input_encoding='utf-8',output_encoding='utf-8')
def template(name):
    return _lookup.get_template(name)

class WebPortal:
    @cherrypy.expose()
    def intro(self,sub=False):
        if sub:
            if sub=='real':
                return '<script>top.%s();</script>'%const.PORTAL_CALLBACK
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
    def finale_change(self,finale,password,timeout):
        if not cherrypy.request.headers.get('referer','').startswith('http://127.0.0.1:%d/'%const.PORTAL_PORT):
            return 'Error: referer invalid. Possible CSRF detected.'
        const.TIMEOUT=int(timeout)
        const.FINALE_URL=finale
        const.PASSWORD=password
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose()
    def proxy_mode_change(self,mode):
        if not cherrypy.request.headers.get('referer','').startswith('http://127.0.0.1:%d/'%const.PORTAL_PORT):
            return 'Error: referer invalid. Possible CSRF detected.'
        if int(mode) not in [0,1,2]:
            return 'Error: bad proxy mode'
        const.PROXY_MODE=int(mode)
        _should_go_direct.cache_clear()
        raise cherrypy.HTTPRedirect('/')


conf={
    'global': {
        'engine.autoreload.on':False,
        'environment':'production',
        'server.socket_host':'127.0.0.1',
        'server.socket_port':const.PORTAL_PORT,
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