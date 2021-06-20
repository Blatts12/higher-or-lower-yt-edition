from django.db import models
import uuid


class YoutubeChannel(models.Model):
    channel_id = models.URLField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    total_views = models.IntegerField(default=0)
    subscribers = models.IntegerField(default=0)
    number_videos = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class YoutubeVideo(models.Model):
    channel = models.ForeignKey(YoutubeChannel, on_delete=models.CASCADE)
    video_id = models.URLField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    number_comments = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def need_update(self):
        return False


class Game(models.Model):
    game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(YoutubeChannel, on_delete=models.CASCADE)
    videos = models.ManyToManyField(YoutubeVideo)
    points = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}".format(self.channel.name, self.points)
