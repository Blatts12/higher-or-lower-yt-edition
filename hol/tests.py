from django.test import TestCase
from django.utils import timezone
import datetime
from .models import YoutubeChannel


class YoutubeChannelTestCase(TestCase):
    channel_id_now = "UCTwehlI2oqu3DXJ87Mu_99w"
    channel_id_day_past = "UC2k0KJH-WynZL5VlXxko5vQ"
    channel_id_day_future = "UCrPseYLGpNygVi34QpGNqpA"

    def setUp(self):
        YoutubeChannel.objects.create(
            channel_id=self.channel_id_now,
            uploads_id="test1",
            title="test",
            views=123,
            subscribers=123,
            thumbnail="https://yt3.ggpht.com/test"
        )

        time = timezone.now() - datetime.timedelta(days=1)
        YoutubeChannel.objects.create(
            channel_id=self.channel_id_day_past,
            uploads_id="test2",
            last_update=time,
            title="test",
            views=123,
            subscribers=123,
            thumbnail="https://yt3.ggpht.com/test"
        )

        time = timezone.now() + datetime.timedelta(days=1)
        YoutubeChannel.objects.create(
            channel_id=self.channel_id_day_future,
            uploads_id="test3",
            last_update=time,
            title="test",
            views=123,
            subscribers=123,
            thumbnail="https://yt3.ggpht.com/test"
        )

    def test_channel_needs_update(self):
        now = YoutubeChannel.objects.get(pk=self.channel_id_now)
        day_past = YoutubeChannel.objects.get(pk=self.channel_id_day_past)
        day_future = YoutubeChannel.objects.get(pk=self.channel_id_day_future)

        print(now.last_update)
        print(day_past.last_update)
        print(day_future.last_update)

        self.assertFalse(now.needs_update())
        self.assertTrue(day_past.needs_update())
        self.assertFalse(day_future.needs_update())
