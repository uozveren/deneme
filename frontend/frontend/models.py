from django.db import models
from django.contrib.auth.models import User

class Feed(models.Model):
    uri = models.CharField(max_length=2000)
    xpath = models.CharField(max_length=2000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    edited = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Field(models.Model):
    name = models.CharField(max_length=200)
    required = models.BooleanField(default=True)

class FeedField(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    xpath = models.CharField(max_length=2000)

class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    md5sum = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = ['feed', 'md5sum']


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"
