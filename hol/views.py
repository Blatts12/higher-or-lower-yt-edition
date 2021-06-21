from decouple import config
import requests
from django.views.generic.edit import FormView
from .forms import NewGameForm


class NewGameView(FormView):
    template_name = "hol/newgame.html"
    form_class = NewGameForm
    success_url = "/hol/game_start/"

    def form_valid(self, form):
        channel_id = form.cleaned_data["channel_id"]
        uploads_id = self.fetch_uploads_id(channel_id)
        if uploads_id is not None:
            uploads = self.fetch_uploads(uploads_id)
            print(len(uploads))
            return super(NewGameView, self).form_valid(form)
        else:
            form.add_error("channel_id", "Invalid channel id")
            return super(NewGameView, self).form_invalid(form)

    def fetch_uploads_id(self, channel_id):
        try:
            res = requests.get(
                "https://www.googleapis.com/youtube/v3/channels?id={}&key={}&part=contentDetails".
                format(channel_id, config("YT_PUBLIC_KEY"))).json()

            return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except KeyError:
            return None

    def fetch_channel(self, channel_id):
        pass

    def fetch_uploads(self, uploads_id):
        uploads = []
        page_token = ""
        key = config("YT_PUBLIC_KEY")

        while page_token is not None:
            res = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems?playlistId={}&key={} \
                &part=snippet&maxResults=50&pageToken={}".
                format(uploads_id, key, page_token)).json()

            uploads += res["items"]
            page_token = res.get("nextPageToken")

        return uploads
