from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Users


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Users
        fields = ("username", "role", )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Users
        fields = ("username", "role",)

class RegisterForm(UserCreationForm):

    class Meta:
        model = Users
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
        labels = {"username": "Nazwa użytkownika", "first_name": "Imię", "last_name": "Nazwisko"}

class AddGameForm(forms.Form):
    title = forms.CharField(label="Tytuł", max_length=200, required=True)
    author = forms.CharField(label="Autor", max_length=200, required=False)
    publisher = forms.CharField(label="Wydawca", max_length=200, required=False)
    min_players = forms.IntegerField(label="Minimalna liczba graczy", required=False, min_value=1)
    max_players = forms.IntegerField(label="Maksymalna liczba graczy", required=False, min_value=1)
    time = forms.CharField(label="Czas gry", max_length=10, required=False)

class SearchGameForm(forms.Form):
    search_phrase = forms.CharField(label="Nazwa gry", max_length=200, required=True)

class AddCommentForm(forms.Form):
    rating = forms.IntegerField(label="Ocena w skali 1-10", required=True, min_value=1, max_value=10)
    comment = forms.CharField(label="Opis", max_length=1000, required=False)