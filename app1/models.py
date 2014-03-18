from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse
import random

GAME_STATUS_CHOICES = (
    ('A', 'Active'),
    ('F', 'Active'),
    ('S', 'Active'),
    ('D', 'Active'),
)

DICE_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('A', 'A'),
    ('H', 'H'),
)

class GamesManager(models.Manager):
    def games_for_user(self, user):
        games = super(GamesManager, self).get_queryset().filter(
            Q(first_player_id=user.id) | Q(second_player_id=user.id))
        return games

class Game(models.Model):
    first_player = models.ForeignKey(User, related_name='game_first_player')
    second_player = models.ForeignKey(User, related_name='game_second_player')
    next_to_move = models.ForeignKey(User, related_name='game_to_move')
    start_time = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, default='A', choices=GAME_STATUS_CHOICES)

    objects = GamesManager()

    def create_move(self):
        return Move(game=self)

    def do_move(self, data):
        last_move = self.move_set.last()
        new_move = self.create_move()
        new_move.roll = last_move.roll + 1
        new_move.turn = last_move.turn

        if 'hold1' in data:
            new_move.dice_1 = last_move.dice_1
        else:
            new_move.dice_1 = random.choice(DICE_CHOICES)[0]

        if 'hold2' in data:
            new_move.dice_2 = last_move.dice_2
        else:
            new_move.dice_2 = random.choice(DICE_CHOICES)[0]

        if 'hold3' in data:
            new_move.dice_3 = last_move.dice_3
        else:
            new_move.dice_3 = random.choice(DICE_CHOICES)[0]

        if 'hold4' in data:
            new_move.dice_4 = last_move.dice_4
        else:
            new_move.dice_4 = random.choice(DICE_CHOICES)[0]

        if 'hold5' in data:
            new_move.dice_5 = last_move.dice_5
        else:
            new_move.dice_5 = random.choice(DICE_CHOICES)[0]

        if 'hold6' in data:
            new_move.dice_6 = last_move.dice_6
        else:
            new_move.dice_6 = random.choice(DICE_CHOICES)[0]

        new_move.save()

    def is_empty(self, hold1, hold2, hold3, hold4, hold5, hold6):
        return

    def as_game(self):
        game = []
        moves = self.move_set.all()
        for move in moves:
            game.append([move.dice_1, move.dice_2, move.dice_3, move.dice_4, move.dice_5, move.dice_6])
        return game

    def get_absolute_url(self):
        return reverse('game_detail', args=[self.id])

    def __unicode__(self):
        return "%s vs %s" % (self.first_player, self.second_player)

class Move(models.Model):
    game = models.ForeignKey(Game)
    turn = models.IntegerField()
    roll = models.IntegerField()
    dice_1 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_2 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_3 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_4 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_5 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_6 = models.CharField(max_length=1, choices=DICE_CHOICES)
    comment = models.CharField(max_length=300)

    def make_move(self, game, data):
        if data['hold1'] == True:
            print "hold1"
        return Move(game=self)

    def __unicode__(self):
        return "Game %s, Turn %s" % (self.game, self.turn)

