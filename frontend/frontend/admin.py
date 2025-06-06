from django.contrib import admin

from .models import Feed, Field, FeedField, Post, Subscription

# Register basic models without custom admin classes
admin.site.register([Feed, Field, FeedField, Post])


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'plan')
    search_fields = ('user__username',)
