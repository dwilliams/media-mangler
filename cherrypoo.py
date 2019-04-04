import os

import cherrypy

app_conf = {
    '/': {
        'tools.gzip.on': True,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.abspath("./static")
    }
}

class Root(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"

if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/', app_conf)
