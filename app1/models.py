from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Max
import random

GAME_STATUS_CHOICES = (
    ('A', 'Active'),
    ('F', 'First player won'),
    ('S', 'Second player won'),
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
    first_player_health = models.IntegerField(default=10)
    second_player_health = models.IntegerField(default=10)
    first_player_points = models.IntegerField(default=0)
    second_player_points = models.IntegerField(default=0)

    objects = GamesManager()

    def first_player_health_percent(self):
        return (self.first_player_health / 10.0) * 100

    def second_player_health_percent(self):
        return (self.second_player_health / 10.0) * 100

    def first_player_points_percent(self):
        return (self.first_player_points / 20.0) * 100

    def second_player_points_percent(self):
        return (self.second_player_points / 20.0) * 100

    def create_move(self):
        return Move(game=self)

    def do_move(self, data):
        last_move = self.move_set.last()
        new_move = self.create_move()
        if last_move:
            new_move.roll = last_move.roll + 1
            if new_move.roll <= 3:
                new_move.turn = last_move.turn
            else:
                # next players first move
                new_move.turn = last_move.turn + 1
                new_move.roll = 1
        else:
            # first move
            new_move.roll = 1
            new_move.turn = 1

        if new_move.roll <= 3:

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
            if new_move.roll == 3:
                self.toggle_next_player()
                self.status = self.get_status()
                self.save()

    def toggle_next_player(self):
        if self.next_to_move == self.first_player:
            self.next_to_move = self.second_player
        else:
            self.next_to_move = self.first_player

    def get_status(self):
        # a move has been made, check the scores...
        final_rolls = self.move_set.filter(roll=3)
        player1_points = 0
        player1_health = 10
        player2_points = 0
        player2_health = 10

        for roll in final_rolls:
            hearts = self.count_dice(roll, 'H')
            attacks = self.count_dice(roll, 'A')
            point_1 = self.count_dice(roll, '1')
            point_2 = self.count_dice(roll, '2')
            point_3 = self.count_dice(roll, '3')

            points = 0
            points += self.count_points(point_1, '1')
            points += self.count_points(point_2, '2')
            points += self.count_points(point_3, '3')

            if roll.turn % 2 != 0:
                # player 1's turn
                player1_points += points
                player1_health += hearts
                player2_health -= attacks
            else:
                # player 2
                player2_points += points
                player2_health += hearts
                player1_health -= attacks

            # you can't get more than 10 health
            if player1_health > 10:
                player1_health = 10
            if player2_health > 10:
                player2_health = 10

        # end game conditions
        if player1_points >= 20 or player2_health <= 0:
            status = "F"
        elif player2_points >= 20 or player1_health <= 0:
            status = "S"
        else:
            status = "A"
        self.first_player_health = player1_health
        self.second_player_health = player2_health
        self.first_player_points = player1_points
        self.second_player_points = player2_points
        return status

    def count_points(self, dice_count, dice_face):
        points = 0
        # you need at least 3 to earn any points
        if dice_count >= 3:
            # earn the face value of the dice
            points += int(dice_face)
            # work out how many remain dice we have
            remaining = dice_count - 3
            # one more point for each match dice
            points += (remaining * 1)
        return points

    def count_dice(self, roll, dice_type):
        count = 0
        if roll.dice_1 == dice_type:
            count += 1
        if roll.dice_2 == dice_type:
            count += 1
        if roll.dice_3 == dice_type:
            count += 1
        if roll.dice_4 == dice_type:
            count += 1
        if roll.dice_5 == dice_type:
            count += 1
        if roll.dice_6 == dice_type:
            count += 1
        return count

    def as_game(self):
        game = []
        moves = self.move_set.all()
        if (moves.count() == 0) or (moves.count() % 3 == 0):
            # make a first roll
            self.do_move('')

        show_moves = self.move_set.filter(roll=3)
        for move in show_moves:
            game.append([move.dice_1, move.dice_2, move.dice_3, move.dice_4, move.dice_5, move.dice_6])

        last_move = self.move_set.last()
        game.append([last_move.dice_1, last_move.dice_2, last_move.dice_3, last_move.dice_4, last_move.dice_5, last_move.dice_6])
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

