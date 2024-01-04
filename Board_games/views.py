from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import AddGameForm, SearchGameForm
from .models import BoardGames
from django.urls import reverse
from django.db.models import Avg

# Create your views here.
def home(response):
    if response.method == 'POST':
        form = SearchGameForm(response.POST)

        if form.is_valid():
            search_phrase = form.cleaned_data['search_phrase']
            return HttpResponseRedirect(reverse('search_game', args=[search_phrase]))
    else:
        form = SearchGameForm()

    return render(response, "Board_games/home.html", {"form": form})

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

def search_game(response, search_phrase):
    result = BoardGames.objects.filter(title__icontains=search_phrase).values('id','title')
    return render(response, "Board_games/search_games.html", {"list": result})

def top_board_games(response):
    result = (BoardGames.objects.annotate(avg_rating=Avg('comments__rating')).values(
        'id','title', 'avg_rating').order_by('-avg_rating'))
    return render(response, "Board_games/top_board_games.html", {"list": result})