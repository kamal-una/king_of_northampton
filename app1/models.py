from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse

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

    def __unicode__(self):
        return "Game %s, Turn %s" % (self.game, self.turn)

