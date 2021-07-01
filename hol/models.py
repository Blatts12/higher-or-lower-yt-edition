from django.db import models
from django.utils import timezone
import uuid
import datetime


class YoutubeChannel(models.Model):
    channel_id = models.CharField(max_length=64, primary_key=True)
    uploads_id = models.CharField(max_length=64, unique=True)
    last_update = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=128)
    views = models.IntegerField(default=0)
    subscribers = models.IntegerField(default=0)
    thumbnail = models.URLField(max_length=128)

    def __str__(self):
        return self.name

    def needs_update(self):
        return self.last_update < timezone.now() - datetime.timedelta(days=1)


class YoutubeVideo(models.Model):
    video_id = models.CharField(max_length=32, primary_key=True)
    channel = models.ForeignKey(YoutubeChannel, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Game(models.Model):
    # game_id is a seed for shuffle
    game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(YoutubeChannel, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    round = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "Round: {}, Points: {}".format(self.round, self.points)
