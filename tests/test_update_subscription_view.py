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
        DEFAULT_PLAN='basic',
    )
    django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from frontend.models import Subscription


def test_update_subscription_plan():
    user = User.objects.create_user('u', password='p')
    client = Client()
    client.force_login(user)
    url = reverse('update_subscription')
    resp = client.post(url, {'plan': 'premium'})
    assert resp.status_code == 302
    sub = Subscription.objects.get(user=user)
    assert sub.plan == 'premium'
    assert sub.status == 'active'
    assert sub.end_date is None


def test_cancel_subscription():
    user = User.objects.create_user('u2', password='p')
    client = Client()
    client.force_login(user)
    url = reverse('update_subscription')
    today = timezone.now().date()
    resp = client.post(url, {'cancel': '1'})
    assert resp.status_code == 302
    sub = Subscription.objects.get(user=user)
    assert sub.status == 'canceled'
    assert sub.end_date == today
