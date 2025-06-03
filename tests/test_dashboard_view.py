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
from frontend.models import Feed


def test_dashboard_filters_by_query():
    user = User.objects.create_user('u', password='p')
    other_user = User.objects.create_user('o', password='p')

    Feed.objects.create(uri='http://example.com/match', xpath='//div', user=user)
    Feed.objects.create(uri='http://nomatch.com/feed', xpath='//div', user=user)
    Feed.objects.create(uri='http://example.com/other', xpath='//div', user=other_user)

    client = Client()
    client.force_login(user)
    url = reverse('dashboard')
    resp = client.get(url, {'q': 'example'})
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert 'http://example.com/match' in content
    assert 'http://nomatch.com/feed' not in content
    assert 'http://example.com/other' not in content
