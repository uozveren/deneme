import urllib.request, urllib.parse, urllib.error
import json
import re

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

from .forms import IndexForm
from .settings import DOWNLOADER_PAGE_URL, FEED_PAGE_URL
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .setup_tool import get_selection_tag_ids, build_xpathes_for_items
from .setup_tool_ext import build_xpath_results
from .models import Feed, Field, FeedField, Subscription

def index(request):
    if request.method == 'GET' and 'url' in request.GET:
        form = IndexForm(request.GET)
        if form.is_valid():
            val = URLValidator()
            try:
                url = request.GET['url']
                if not url.startswith('http'):
                    url = 'http://' + url
                val(url)
            except ValidationError as e:
                form.add_error('url', 'Invalid url')
            else:
                return HttpResponseRedirect('%s?url=%s' % (reverse('setup'), urllib.parse.quote(url.encode('utf8'))))
    else:
        form = IndexForm()

    return render(request, 'frontend/index.html', {'form': form})

def contact(request):
    return render(request, 'frontend/contact.html')

@ensure_csrf_cookie
def setup(request):
    if request.method == 'GET' and 'url' in request.GET:
        external_page_url = DOWNLOADER_PAGE_URL + urllib.parse.quote(request.GET['url'], safe='')
        return render(request, 'frontend/setup.html',
                        {
                            'external_page_url': external_page_url,
                            'page_url': request.GET['url']
                        })

    return HttpResponseBadRequest('Url is required')

def _validate_html(html):

    def walk(tag):
        if (len(tag) != 3 or not isinstance(tag[0], str) or
                type(tag[1]) is not dict or 'tag-id' not in tag[1] or
                type(tag[2]) is not list):
            return False
        for t in tag[2]:
            if not walk(t):
                return False
        return True

    return walk(html)


def setup_get_selected_ids(request):
    if request.method == 'POST':
        obj = json.loads(request.body)
        if 'html' not in obj or 'names' not in obj:
            return HttpResponseBadRequest('"html" and "names" parameters are required')
        html_json = obj['html']
        item_names = obj['names']

        if not _validate_html(html_json):
            return HttpResponseBadRequest('html is invalid')

        xpathes = build_xpathes_for_items(item_names, html_json)
        if 'title' in xpathes[1]:
            xpathes[1]['link'] = _get_link_xpath(xpathes[1]['title'])

        resp = {
            'xpathes': xpathes,
            'ids': get_selection_tag_ids(item_names, html_json)
        }

        return HttpResponse(json.dumps(resp))

def _get_link_xpath(title_xpath):
    if title_xpath == './child::node()':
        return './ancestor-or-self::node()/@href'
    else:
        xpath = title_xpath[:len(title_xpath)-len('/child::node()')]
        return xpath +'/ancestor-or-self::node()/@href'

_BASIC_TITLE_ID=1
_BASIC_DESCRIPTION_ID=2
_BASIC_LINK_ID=3

def _create_feed(url, xpathes, user=None, edited=False):
    feed_xpath = xpathes[0]
    item_xpathes = xpathes[1]

    feed = Feed(uri=url, xpath=feed_xpath, user=user, edited=edited)
    feed.save()

    fields = Field.objects.all()

    for field in fields:
        if field.id == _BASIC_LINK_ID and _BASIC_TITLE_ID in item_xpathes and not edited:
            ff = FeedField(feed=feed, field=field, xpath= _get_link_xpath(item_xpathes[_BASIC_TITLE_ID][0]))
            ff.save()
        elif field.id in item_xpathes:
            ff = FeedField(feed=feed, field=field, xpath=item_xpathes[field.id][0])
            ff.save()

    return feed.id

@login_required
def setup_create_feed(request):
    if request.method == 'POST':
        obj = json.loads(request.body)
        if 'html' not in obj or 'names' not in obj or 'url' not in obj:
            return HttpResponseBadRequest('"html", "names" and "url" parameters are required')
        html_json = obj['html']
        item_names = obj['names']
        url = obj['url']

        if not _validate_html(html_json):
            return HttpResponseBadRequest('html is invalid')

        xpathes = build_xpathes_for_items(item_names, html_json)

        field_xpathes = {}
        required = True
        if 'title' in xpathes[1]:
            field_xpathes[_BASIC_TITLE_ID] = [xpathes[1]['title'], required]
        if 'description' in xpathes[1]:
            field_xpathes[_BASIC_DESCRIPTION_ID] = [xpathes[1]['description'], required]
        xpathes[1] = field_xpathes

        feed_id = _create_feed(url, xpathes, request.user)

        return HttpResponse(reverse('preview', args=(feed_id,)))

def _validate_selectors(selectors):
    if not isinstance(selectors, list) or len(selectors) != 2:
        return False
    feed_xpath = selectors[0]
    item_xpathes = selectors[1]

    if not isinstance(feed_xpath, str):
        return False
    if not isinstance(item_xpathes, dict):
        return False

    item_xpathes = {int(field_id): xpath for field_id, xpath in item_xpathes.items()}

    fields = Field.objects.all()

    item_xpathes_out = {}

    for field in fields:
        if field.id in item_xpathes:
            if not isinstance(item_xpathes[field.id], str):
                return False
            else:
                item_xpathes_out[field.id] = [item_xpathes[field.id], field.required]
    return [feed_xpath, item_xpathes_out]

def setup_validate_selectors(request):
    if request.method == 'POST':
        obj = json.loads(request.body)
        if 'selectors' not in obj or 'snapshot_time' not in obj:
            return HttpResponseBadRequest('"selectors" and "snapshot_time" are required')

        selectors = obj['selectors']
        file_name = obj['snapshot_time']

        if not re.match('^\d{10}\.\d+_[\da-f]{32}', file_name):
            return HttpResponseBadRequest('"snapshot_time" is invalid')

        validated_selectors = _validate_selectors(selectors)

        if not validated_selectors:
            return HttpResponseBadRequest('selectors are invalid')

        messages, posts, success = build_xpath_results(validated_selectors, file_name)

        return HttpResponse(json.dumps({'success': success, 'messages': messages, 'posts': posts}))

@login_required
def setup_create_feed_ext(request):
    if request.method == 'POST':
        obj = json.loads(request.body)
        if 'selectors' not in obj or 'snapshot_time' not in obj or 'url' not in obj:
            return HttpResponseBadRequest('"selectors", "snapshot_time" and "url" are required')

        selectors = obj['selectors']
        file_name = obj['snapshot_time']

        if not re.match('^\d{10}\.\d+_[\da-f]{32}', file_name):
            return HttpResponseBadRequest('"snapshot_time" is invalid')

        validated_selectors = _validate_selectors(selectors)

        if not validated_selectors:
            return HttpResponseBadRequest('selectors are invalid')

        messages, posts, success = build_xpath_results(validated_selectors, file_name)

        if success:
            url = obj['url']
            feed_id = _create_feed(url, validated_selectors, request.user, True)
            return HttpResponse(json.dumps({'success': True, 'url': reverse('preview', args=(feed_id,))}))
        else:
            return HttpResponse(json.dumps({'success': False, 'messages': messages}))

def preview(request, feed_id):
    if request.method == 'GET': 
        return render(request, 'frontend/preview.html',
                        {
                            'feed_url': FEED_PAGE_URL + feed_id
                        })

    return HttpResponseBadRequest('Only GET method supported')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    feeds = Feed.objects.filter(user=request.user)
    query = request.GET.get('q')
    if query:
        feeds = feeds.filter(uri__icontains=query)
    feeds = feeds.order_by('-created')
    return render(request, 'frontend/dashboard.html', {'feeds': feeds})


@login_required
def delete_feed(request, feed_id):
    if request.method == 'POST':
        feed = get_object_or_404(Feed, id=feed_id, user=request.user)
        feed.delete()
    return HttpResponseRedirect(reverse('dashboard'))


@login_required
def edit_feed(request, feed_id):
    feed = get_object_or_404(Feed, id=feed_id, user=request.user)
    feed_fields = FeedField.objects.filter(feed=feed).select_related('field')

    config = [feed.xpath, {}]
    for ff in feed_fields:
        config[1][ff.field.name] = ff.xpath

    external_page_url = DOWNLOADER_PAGE_URL + urllib.parse.quote(feed.uri, safe='')

    return render(request, 'frontend/setup.html', {
        'external_page_url': external_page_url,
        'page_url': feed.uri,
        'feed_config_json': json.dumps(config),
    })


@login_required
def manage_subscription(request):
    subscription = get_object_or_404(Subscription, user=request.user)
    return render(request, 'frontend/subscription.html', {
        'subscription': subscription,
    })


@login_required
def update_subscription(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method supported')

    subscription = get_object_or_404(Subscription, user=request.user)

    if 'cancel' in request.POST:
        subscription.status = 'canceled'
        subscription.end_date = timezone.now().date()
        subscription.save()
    elif 'plan' in request.POST:
        subscription.plan = request.POST['plan']
        subscription.status = 'active'
        subscription.end_date = None
        subscription.save()

    return HttpResponseRedirect(reverse('manage_subscription'))
