from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .forms import AddGameForm, SearchGameForm, RegisterForm, AddCommentForm
from .models import BoardGames, Comments, GamesCollection
from django.urls import reverse
from django.db.models import Avg
from datetime import datetime
import json

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
    if response.user.is_authenticated:
        is_game_in_collection = response.user.gamescollection_set.filter(game_id=game.id).exists()
        is_comment_exists = response.user.comments_set.filter(game_id=game.id).exists()
        return render(response, "Board_games/board_games.html", {"game": game, "is_game_in_collection": is_game_in_collection, "is_comment_exists": is_comment_exists})
    return render(response, "Board_games/board_games.html",{"game": game})

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

def top_games(response):
    result = (BoardGames.objects.annotate(avg_rating=Avg('comments__rating')).values(
        'id','title', 'avg_rating').order_by('-avg_rating'))
    return render(response, "Board_games/top_games.html", {"list": result})

def register(response):
    if response.method == 'POST':
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        else:
            return render(response, 'Board_games/error.html', {"message": "Błąd rejestracji"})
    else:
        form = RegisterForm()

    return render(response, "Board_games/register.html", {"form":form})

def games_collection(response):
    return render(response, "Board_games/games_collection.html", )

def add_comment(response, game_id):
    if response.method == "POST":
        form = AddCommentForm(response.POST)

        if form.is_valid():
            rating = form.cleaned_data['rating']
            comment = form.cleaned_data['comment']

            new_comment = Comments(comment=comment, rating=rating, user=response.user, game_id=game_id,
                                   comment_date=datetime.today().strftime('%Y-%m-%d'))
            new_comment.save()

            return HttpResponseRedirect("/board_games/%i" %game_id)
    else:
        form = AddCommentForm()

    game = BoardGames.objects.get(id=game_id)
    if_exist = response.user.comments_set.filter(game_id=game_id).exists()
    if if_exist:
        return render(response, 'Board_games/error.html', {"message": "Już dodałeś opinię dla tej gry"})
    return render(response, "Board_games/add_comment.html", {"form": form, "game": game,
                                                             "if_exist": if_exist})


def add_to_collection(response, game_id):
    if response.method == "POST":
        if response.user.is_authenticated:
            if response.user.gamescollection_set.filter(game_id=game_id).exists():
                return render(response, 'Board_games/error.html', {"message": "Masz już tę grę w kolekcji"})
            else:
                new_collection = GamesCollection(game_id=game_id, user_id=response.user.id,
                                                 purchase_date=datetime.today().strftime('%Y-%m-%d'))
                new_collection.save()
                return HttpResponseRedirect("/board_games/%i" %game_id)

        return render(response, 'Board_games/error.html', {"message": "Najpierw musisz się zalogować"})
    return render(response, 'Board_games/error.html', {"message": "Nie masz dostępu do tej strony"})


def error(response, message):
    return render(response, "Board_games/error.html", {"message": message})

def delete_comment(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comments.objects.get(id=comment_id)
            comment.delete()
            return JsonResponse({'success': True})
        except Comments.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Comment does not exist'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})