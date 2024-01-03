from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import AddGameForm
from .models import BoardGames

example_list = [1,2,3,4,5]

# Create your views here.
def home(response):
    return render(response, "Board_games/home.html", {})

def board_games(response, id):
    game = BoardGames.objects.get(id=id)
    return render(response, "Board_games/board_games.html", {"game": game})

def add_game(response):
    if response.method == "POST":
        form = AddGameForm(response.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            publisher = form.cleaned_data['publisher']
            min_players = form.cleaned_data['min_players']
            max_players = form.cleaned_data['max_players']
            time = form.cleaned_data['time']
            game = BoardGames(title=title, author=author, publisher=publisher, min_players=min_players,
                              max_players=max_players, time=time)
            game.save()

        return HttpResponseRedirect("/board_games/%i" %game.id)

    else:
        form = AddGameForm()
    return render(response, "Board_games/add_game.html", {"form": form})