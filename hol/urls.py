from django.urls import path
from .views import new_game, game

app_name = "hol"
urlpatterns = [
    # path("game/<str:game_id>/"),
    path("game/", game, name="game"),
    path("game_start/", new_game, name="new_game"),
]
