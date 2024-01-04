from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Users


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Users
        fields = ("nickname", "role",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Users
        fields = ("nickname", "role",)


class AddGameForm(forms.Form):
    title = forms.CharField(label="Tytuł", max_length=200, required=True)
    author = forms.CharField(label="Autor", max_length=200, required=False)
    publisher = forms.CharField(label="Wydawca", max_length=200, required=False)
    min_players = forms.IntegerField(label="Minimalna liczba graczy", required=False)
    max_players = forms.IntegerField(label="Maksymalna liczba graczy", required=False)
    time = forms.CharField(label="Czas gry", max_length=10, required=False)