from decouple import config
import requests
from django.views.generic.edit import FormView
from .forms import NewGameForm


class NewGameView(FormView):
    template_name = "hol/newgame.html"
    form_class = NewGameForm
    success_url = "/hol/game_start/"

    def form_valid(self, form):
        print(form.cleaned_data)

        id_response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels?id={}&key={}&part=contentDetails".
            format(form.cleaned_data["channel_id"], config("YT_PUBLIC_KEY")))

        uploads_id = id_response.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        up_response = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems?playlistId={}&key={}&part=snippet&maxResults=50".
            format(uploads_id, config("YT_PUBLIC_KEY")))

        print(up_response.json())

        return super().form_valid(form)
