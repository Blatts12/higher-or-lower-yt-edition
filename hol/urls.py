from django.urls import path
from .views import NewGameView

app_name = "hol"
urlpatterns = [
    # path("game/<str:game_id>/"),
    path("game_start/", NewGameView.as_view(), name="new_game"),
]
