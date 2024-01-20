# Generated by Django 5.0.1 on 2024-01-20 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Board_games', '0002_remove_users_nickname_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='user_groups', to='auth.group'),
        ),
    ]
