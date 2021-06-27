from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers
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
                try:
                    youtube_video = YoutubeVideo.objects.get(
                        video_id=upload["snippet"]["resourceId"]["videoId"])
                    youtube_video.title = upload["snippet"]["title"]
                    youtube_video.views = video_info["statistics"]["viewCount"]
                except YoutubeVideo.DoesNotExist:
                    YoutubeVideo.objects.create(
                        video_id=upload["snippet"]["resourceId"]["videoId"],
                        channel=youtube_channel,
                        title=upload["snippet"]["title"],
                        views=video_info["statistics"]["viewCount"]
                    )

            page_token = res.get("nextPageToken")

    def get_youtube_channel(channel_id):
        try:
            return YoutubeChannel.objects.get(channel_id=channel_id)
        except YoutubeChannel.DoesNotExist:
            return None

    if request.method == "POST":
        form = NewGameForm(request.POST)
        if form.is_valid():
            channel_id = form.cleaned_data["channel_id"]
            youtube_channel = get_youtube_channel(channel_id)

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
                    fetch_uploads(youtube_channel)
                else:
                    return render(request, "hol/newgame.html", {
                        "form": form,
                        "error_message": "Wrong channel id"
                    })
            elif youtube_channel.needs_update():
                fetch_uploads(youtube_channel)

            game = Game(channel=youtube_channel)
            game.save()

            return redirect("/hol/game/{}".format(game.game_id))

    form = NewGameForm()
    return render(request, "hol/newgame.html", {"form": form})


def game(request, game_id):
    if request.method == "GET":
        game = get_object_or_404(Game, pk=game_id)
        channel = game.channel
        videos = list(channel.youtubevideo_set.all())
        random.seed(game_id)
        random.shuffle(videos)

        vid_len = len(videos)
        index_1 = game.round % vid_len
        index_2 = (index_1 + 1) % vid_len

        return render(request, "hol/game.html", {
            "game": game,
            "channel": game.channel,
            "video_1": videos[index_1],
            "video_2": videos[index_2],
        })


def game_progress(request, game_id):
    if request.method == "GET":
        game = get_object_or_404(Game, pk=game_id)
        progress = request.GET.get("progress")
        videos = list(game.channel.youtubevideo_set.all())
        random.seed(game_id)
        random.shuffle(videos)

        vid_len = len(videos)
        index_1 = game.round % vid_len
        index_2 = (index_1 + 1) % vid_len

        video_1 = videos[index_1]
        video_2 = videos[index_2]

        data = {}

        if progress == "higher":
            if video_2.views >= video_1.views:
                data["result"] = "win"
            else:
                data["result"] = "lose"
        else:  # lower
            if video_2.views <= video_1.views:
                data["result"] = "win"
            else:
                data["result"] = "lose"

        video_1 = video_2
        video_2 = videos[(index_2 + 1) % vid_len]

        json_videos = serializers.serialize("json", [video_1, video_2])
        data["video_1"] = json_videos[0]
        data["video_2"] = json_videos[1]

        return JsonResponse(data)
