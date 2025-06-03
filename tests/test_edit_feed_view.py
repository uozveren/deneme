import os
import pytest

django = pytest.importorskip('django')
from django.conf import settings

if not settings.configured:
    settings.configure(
        SECRET_KEY='test',
        ROOT_URLCONF='frontend.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'frontend.apps.FrontendConfig',
        ],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        MIDDLEWARE=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True}],
        STATIC_URL='/static/',
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from frontend.models import Feed, Field, FeedField


def test_edit_feed_prefills_selectors():
    user = User.objects.create_user('u', password='p')

    title = Field.objects.create(id=1, name='title', required=True)
    description = Field.objects.create(id=2, name='description', required=False)
    link = Field.objects.create(id=3, name='link', required=True)

    feed = Feed.objects.create(uri='http://example.com', xpath='//div', user=user)
    FeedField.objects.create(feed=feed, field=title, xpath='./a/text()')
    FeedField.objects.create(feed=feed, field=link, xpath='./a/@href')
    FeedField.objects.create(feed=feed, field=description, xpath='./p/text()')

    client = Client()
    client.force_login(user)
    url = reverse('edit_feed', args=[feed.id])
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert './a/text()' in content
    assert './p/text()' in content
