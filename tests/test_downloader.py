import os

from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, defer, endpoints
from twisted.logger import Logger

from pol.log import LogHandler
from pol.server import Server


class MFTests(object):

    def __init__(self):
        self.log = Logger()

    def start_static(self):
        """Start a static file server for the sample pages."""
        pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
        resource = File(pages_dir)
        factory = Site(resource)
        endpoint = endpoints.TCP4ServerEndpoint(reactor, 0)
        d = endpoint.listen(factory)

        def store_port(port):
            self.static_port = port.getHost().port
            return port

        d.addCallback(store_port)
        return d

    def send_request(self, path='/index.html'):
        from twisted.web.client import Agent, readBody

        url = 'http://127.0.0.1:%d%s' % (self.static_port, path)
        agent = Agent(reactor)
        d = agent.request(b'GET', url.encode('ascii'))
        d.addCallback(readBody)
        return d

    def stop_callback(self, none):
        reactor.stop()

    def test_log_handler(self):
        handler = LogHandler()
        self.log.info('Test msg with {parameter} is OK', parameter="value")
        self.log.error('Test error with {parameter} is OK', parameter="value")
        self.log.error('Test error with {parameter} (isError={isError}) is OK', parameter="value", isError=False)
        self.log.error('Test error with {parameter} (isError={isError}) is OK', parameter="value", isError=True)

        d = defer.Deferred()
        reactor.callLater(0, d.callback, None)
        d.addCallback(self.stop_callback)
        d.addErrback(lambda err: print("callback error: %s\ncallback traceback: %s" % (err.getErrorMessage(), err.getTraceback())))

        reactor.run()

    def test_static_server(self):
        d = self.start_static()
        d.addCallback(lambda _: self.send_request('/index.html'))

        def check_body(body):
            if b'Index Page' not in body:
                raise AssertionError('Index page not served')

        d.addCallback(check_body)
        d.addCallback(self.stop_callback)
        d.addErrback(lambda err: print("callback error: %s\ncallback traceback: %s" % (getattr(err, 'getErrorMessage', lambda: err)(), getattr(err, 'getTraceback', lambda: '')())))

        reactor.run()

    def test_server(self):
        d = defer.Deferred()
        reactor.callLater(3, d.callback, None)
        d.addCallback(self.stop_callback)
        #d.addCallback(self.send_request)
        d.addErrback(lambda err: print("callback error: %s\ncallback traceback: %s" % (err.getErrorMessage(), err.getTraceback())))

        Server(port=1234, db_creds=None, snapshot_dir='~/tmp', user_agent='', debug=False).run()


