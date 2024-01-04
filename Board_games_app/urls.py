"""
URL configuration for Board_games_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from Board_games import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("board_games/<int:id>/", views.board_games, name="board_games"),
    path("add_game/", views.add_game, name="add_game"),
    path("search_game/<str:search_phrase>", views.search_game, name="search_game"),
    path("top_games", views.top_games, name="top_games"),
    path("register/", views.register, name="register"),
    path("", include("django.contrib.auth.urls")),
    path("games_collection/", views.games_collection, name="games_collection")
]
