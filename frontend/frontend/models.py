from django.db import models
from django.contrib.auth.models import User

class Feed(models.Model):
    uri = models.CharField(max_length=2000)
    xpath = models.CharField(max_length=2000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    edited = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a human readable representation of the feed."""
        return self.uri

class Field(models.Model):
    name = models.CharField(max_length=200)
    required = models.BooleanField(default=True)

    def __str__(self):
        """Return the name of the field."""
        return self.name

class FeedField(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    xpath = models.CharField(max_length=2000)

    def __str__(self):
        """Describe which field belongs to which feed."""
        feed_str = getattr(self.feed, 'uri', str(self.feed))
        field_str = getattr(self.field, 'name', str(self.field))
        return f"{feed_str} - {field_str}"

class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    md5sum = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = ['feed', 'md5sum']

    def __str__(self):
        """Return a representation including feed and checksum."""
        feed_str = getattr(self.feed, 'uri', str(self.feed))
        return f"{feed_str} - {self.md5sum}"


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
