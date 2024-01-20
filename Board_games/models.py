from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q


class Roles(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Roles'




class Users(AbstractUser):
    first_name = models.CharField(max_length=32, blank=True, null=True)
    last_name = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Roles, on_delete=models.PROTECT, db_column='role_id')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'Users'


class BoardGames(models.Model):
    title = models.TextField()
    author = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)
    min_players = models.IntegerField(blank=True, null=True)
    max_players = models.IntegerField(blank=True, null=True)
    time = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Board_games'


class GamesCollection(models.Model):
    game = models.ForeignKey(BoardGames, on_delete=models.CASCADE, db_column='game_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    purchase_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'Games_collection'
        constraints = [UniqueConstraint(fields=['game', 'user'], name='unique_collection')]


class Comments(models.Model):
    game = models.ForeignKey(BoardGames, on_delete=models.CASCADE, db_column='game_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    comment_date = models.DateField()

    UniqueConstraint(fields=['game', 'user'], name='unique_comment')
    CheckConstraint(check=Q(rating__gte=0) & Q(rating__lte=10), name='comments_rating_range',)

    class Meta:
        db_table = 'Comments'
