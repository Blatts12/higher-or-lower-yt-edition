from django.shortcuts import render, redirect
from decouple import config
import random
import requests
from .forms import NewGameForm
from .models import Game, YoutubeChannel, YoutubeVideo

# UCrPseYLGpNygVi34QpGNqpA  - Ludwig
# UCNMyf6eTspYWPBm84VOqLkA  - shafter
# UCTwehlI2oqu3DXJ87Mu_99w  - me
# youtube data api v3
video_link = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id={}&key={}"
channel_link = "https://www.googleapis.com/youtube/v3/channels?id={}&key={}&\
part=contentDetails,snippet,statistics"
ups_link = "https://www.googleapis.com/youtube/v3/playlistItems?playlistId={}&key={}\
&part=snippet&maxResults=50&pageToken={}"


def new_game(request):

    def fetch_channel_info(channel_id):
        try:
            res = requests.get(channel_link.format(channel_id, config("YT_PUBLIC_KEY"))).json()
            channel = res["items"][0]
            return {
                "uploads_id": channel["contentDetails"]["relatedPlaylists"]["uploads"],
                "thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
                "title": channel["snippet"]["title"],
                "subscriberCount": channel["statistics"]["subscriberCount"],
                "viewCount": channel["statistics"]["viewCount"],
            }
        except KeyError:
            return None

    def fetch_video_info(video_id):
        res = requests.get(video_link.format(video_id, config("YT_PUBLIC_KEY"))).json()
        return res["items"][0]

    def fetch_uploads(youtube_channel):
        page_token = ""
        key = config("YT_PUBLIC_KEY")
        uploads_id = youtube_channel.uploads_id

        while page_token is not None:
            res = requests.get(ups_link.format(uploads_id, key, page_token)).json()

            for upload in res["items"]:
                video_info = fetch_video_info(upload["snippet"]["resourceId"]["videoId"])
                YoutubeVideo.objects.update_or_create(
                    video_id=upload["snippet"]["resourceId"]["videoId"],
                    channel=youtube_channel,
                    title=upload["snippet"]["title"],
                    views=video_info["statistics"]["viewCount"]
                )

            page_token = res.get("nextPageToken")

    if request.method == "POST":
        form = NewGameForm(request.POST)
        if form.is_valid():
            channel_id = form.cleaned_data["channel_id"]
            need_video_update = True
            try:
                youtube_channel = YoutubeChannel.objects.get(channel_id=channel_id)
            except YoutubeChannel.DoesNotExist:
                youtube_channel = None

            if youtube_channel is None:
                channel_info = fetch_channel_info(channel_id)
                if channel_info is not None:
                    youtube_channel = YoutubeChannel(
                        channel_id=channel_id,
                        uploads_id=channel_info["uploads_id"],
                        title=channel_info["title"],
                        views=channel_info["viewCount"],
                        subscribers=channel_info["subscriberCount"],
                        thumbnail=channel_info["thumbnail"]
                    )
                    youtube_channel.save()
                else:
                    return render(request, "hol/newgame.html", {
                        "form": form,
                        "error_message": "Wrong channel id"
                    })
            else:
                need_video_update = youtube_channel.needs_update()

            if need_video_update:
                fetch_uploads(youtube_channel)

            game = Game(channel=youtube_channel)
            game.save()

            return redirect("/hol/game/{}".format(game.game_id))

    form = NewGameForm()
    return render(request, "hol/newgame.html", {"form": form})


def game(request, game_id):
    if request.method == "POST":
        return redirect("/hol/game_start")
    else:
        game = Game.objects.get(game_id=game_id)
        channel = game.channel
        videos = list(channel.youtubevideo_set.all())
        random.seed(game_id)
        random.shuffle(videos)

        return render(request, "hol/game.html", {
            "game": game,
            "channel": game.channel,
            "videos": videos
        })
