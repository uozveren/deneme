import json
import datetime
import pytest

# Skip tests if optional dependencies are missing
pytest.importorskip('w3lib')
pytest.importorskip('scrapy')
pytest.importorskip('feedgenerator')
pytest.importorskip('lxml')

from pol.feed import Feed
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


def test_build_feed(monkeypatch):
    selector = Selector(text=SAMPLE_HTML)
    feed = Feed({})
    monkeypatch.setattr(feed, 'fill_time', _fake_fill_time.__get__(feed))

    rss_str, item_cnt, new_cnt = feed.buildFeed(selector, SAMPLE_HTML, FEED_CONFIG)

    assert item_cnt == 2
    assert new_cnt == 2

    root = etree.fromstring(rss_str)
    titles = [el.text for el in root.xpath('//item/title')]
    assert titles == ['Post 1', 'Post 2']
    links = [el.text for el in root.xpath('//item/link')]
    assert links[0] == 'http://example.com/post1.html'
    assert links[1] == 'http://example.com/post2.html'
