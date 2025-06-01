import json
import datetime
import pytest

pytest.importorskip('w3lib')
pytest.importorskip('scrapy')
pytest.importorskip('feedgenerator')
pytest.importorskip('lxml')
pytest.importorskip('twisted')

from pol.feed import Feed
from pol.server import Site
from scrapy.selector import Selector
from lxml import etree

HTML_PATH = 'tests/pages/feed_sample.html'

with open(HTML_PATH) as f:
    SAMPLE_HTML = f.read()

FEED_CONFIG = {
    'id': 1,
    'uri': 'http://example.com/index.html',
    'xpath': "//div[@class='entry']",
    'fields': {
        'title': "./a[@class='title']/text()",
        'link': "./a[@class='title']/@href",
        'description': "./p[@class='desc']/text()",
    },
    'required': {
        'title': True,
        'link': True,
        'description': False,
    },
}


def _fake_fill_time(self, feed_id, items):
    now = datetime.datetime(2023, 1, 1)
    for i, item in enumerate(items):
        item['time'] = now + datetime.timedelta(minutes=i)
    return len(items)


def _fake_start_request(self, request, url, feed_config=None, selector_defer=None, sanitize=False, response_format='xml'):
    selector = Selector(text=SAMPLE_HTML)
    rss_str, item_cnt, new_cnt = self.feed.buildFeed(selector, SAMPLE_HTML, feed_config)
    if response_format == 'json':
        items = []
        root = etree.fromstring(rss_str)
        for item_el in root.xpath('//item'):
            data = {child.tag: (child.text or '') for child in item_el}
            items.append(data)
        rss_str = json.dumps(items)
        request.setHeader(b'Content-Type', b'application/json; charset=utf-8')
    else:
        request.setHeader(b'Content-Type', b'text/xml; charset=utf-8')
    request.write(rss_str.encode('utf-8'))
    request.finish()


class DummyClient:
    host = '127.0.0.1'


class DummyRequest:
    def __init__(self, uri, args=None):
        self.uri = uri
        self.args = args or {}
        self.headers = {}
        self.written = b''
        self.finished = False
        self.code = None

    def getHeader(self, name):
        return None

    @property
    def client(self):
        return DummyClient()

    def setHeader(self, k, v):
        self.headers[k] = v

    def setResponseCode(self, code):
        self.code = code

    def write(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.written += data

    def finish(self):
        self.finished = True


def _setup_site(monkeypatch):
    site = Site({}, None, 'agent')
    site.feed = Feed({})
    monkeypatch.setattr(site.feed, 'fill_time', _fake_fill_time.__get__(site.feed))
    monkeypatch.setattr(site.feed, 'getFeedData', lambda fid: ('http://example.com/index.html', FEED_CONFIG))
    monkeypatch.setattr(site, 'startRequest', _fake_start_request.__get__(site))
    return site


def test_feed_endpoint_xml(monkeypatch):
    site = _setup_site(monkeypatch)
    req = DummyRequest(b'/feed/1')
    site.render_GET(req)
    assert req.finished
    assert b'<rss' in req.written
    root = etree.fromstring(req.written)
    assert root.xpath('//item/title')[0].text == 'Post 1'


def test_feed_endpoint_json(monkeypatch):
    site = _setup_site(monkeypatch)
    req = DummyRequest(b'/feed/1', args={b'format': [b'json']})
    site.render_GET(req)
    assert req.finished
    assert req.headers.get(b'Content-Type', b'').startswith(b'application/json')
    data = json.loads(req.written.decode('utf-8'))
    assert data[0]['title'] == 'Post 1'
