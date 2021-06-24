from django.shortcuts import render, redirect
from decouple import config
import requests
from .forms import NewGameForm

# UCrPseYLGpNygVi34QpGNqpA  - Ludwig
# UCNMyf6eTspYWPBm84VOqLkA  - shafter
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
                "channel_id": channel_id,
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

    def fetch_uploads(uploads_id):
        uploads = []
        page_token = ""
        key = config("YT_PUBLIC_KEY")

        while page_token is not None:
            res = requests.get(ups_link.format(uploads_id, key, page_token)).json()

            for upload in res["items"]:
                video_info = fetch_video_info(upload["snippet"]["resourceId"]["videoId"])
                uploads.append({
                    "title": upload["snippet"]["title"],
                    "date": upload["snippet"]["publishedAt"],
                    "thumbnail": upload["snippet"]["thumbnails"]["high"]["url"],
                    "views": video_info["statistics"]["viewCount"],
                })

            page_token = res.get("nextPageToken")

        return uploads

    if request.method == "POST":
        form = NewGameForm(request.POST)
        if form.is_valid():
            channel_id = form.cleaned_data["channel_id"]
            channel_info = fetch_channel_info(channel_id)

            if channel_info is not None:
                uploads = fetch_uploads(channel_info["uploads_id"])

            request.session["game_data"] = {
                "channel_info": channel_info,
                "uploads": uploads,
            }
            return redirect("/hol/game")

    else:
        form = NewGameForm()

    return render(request, "hol/newgame.html", {"form": form})


def game(request):
    if request.method == "POST":
        return redirect("/hol/game/")

    return render(request, "hol/game.html")
