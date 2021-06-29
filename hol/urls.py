from django.urls import path
from . import views


app_name = "hol"
urlpatterns = [
    path("game_start/", views.new_game, name="new_game"),
    path("game/<str:game_id>/", views.game, name="game"),
    path("game/<str:game_id>/progress/", views.game_progress, name="game_progress"),
]
