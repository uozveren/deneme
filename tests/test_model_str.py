import pytest

django = pytest.importorskip('django')
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'frontend.apps.FrontendConfig',
        ],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        SECRET_KEY='test',
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    django.setup()

from frontend.models import Feed, Field, FeedField, Post


def test_feed_str():
    feed = Feed(uri='http://example.com', xpath='//item')
    assert str(feed) == 'http://example.com'


def test_field_str():
    field = Field(name='title', required=True)
    assert str(field) == 'title'


def test_feedfield_str():
    feed = Feed(uri='http://example.com', xpath='//item')
    field = Field(name='title', required=True)
    ff = FeedField(feed=feed, field=field, xpath='.')
    assert str(ff) == 'http://example.com - title'


def test_post_str():
    feed = Feed(uri='http://example.com', xpath='//item')
    post = Post(feed=feed, md5sum='abc123')
    assert str(post) == 'http://example.com - abc123'
