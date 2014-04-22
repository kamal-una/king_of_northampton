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
        first_games = super(GamesManager, self).get_query_set().filter(first_player_id=user.id)
        second_games = super(GamesManager, self).get_query_set().filter(second_player_id=user.id)
        return first_games, second_games

    def new_game(self, invitation):
        game = Game(first_player=invitation.to_user,
                    second_player=invitation.from_user,
                    next_to_move=invitation.to_user)
        return game

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

    def my_move(self, user):
        if self.next_to_move == user:
            return True
        else:
            return False

    def get_last_move(self):
        try:
            return self.move_set.order_by('-turn','-roll')[:1].get()
        except:
            return None

    def do_move(self, data):
        last_move = self.get_last_move()

        new_move = self.create_move()
        new_move.player = self.next_to_move
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
                # we pass the last_move, so we don't rely on getting it from the datastore
                self.status = self.get_status(new_move)

        return new_move

    def toggle_next_player(self):
        if self.next_to_move == self.first_player:
            self.next_to_move = self.second_player
        else:
            self.next_to_move = self.first_player

    def get_status(self, last_move):
        # a whole move has been made, go through each move to check the scores...
        final_rolls = self.move_set.filter(roll=3).order_by('turn')
        self.first_player_points = 0
        self.first_player_health = 10
        self.second_player_points = 0
        self.second_player_health = 10

        for roll in final_rolls:
            # if we do get the last_move from the datastore, ignore it...
            if roll.turn != last_move.turn:
                self.process_turn(roll)

        # now process the last move from memory
        self.process_turn(last_move)

        # end game conditions
        if self.first_player_points >= 20 or self.second_player_health <= 0:
            self.status = "F"
        elif self.second_player_points >= 20 or self.first_player_health <= 0:
            self.status = "S"
        else:
            self.status = "A"

        self.save()
        
        return self.status

    def process_turn(self, roll):
        hearts = self.count_dice(roll, 'H')
        attacks = self.count_dice(roll, 'A')
        point_1 = self.count_dice(roll, '1')
        point_2 = self.count_dice(roll, '2')
        point_3 = self.count_dice(roll, '3')

        points = 0
        points += self.count_points(point_1, '1')
        points += self.count_points(point_2, '2')
        points += self.count_points(point_3, '3')

        #if roll.player == self.first_player:
        # this will allow you to play against yourself
        if roll.turn % 2 != 0:
            # player 1's turn
            self.first_player_points += points
            self.first_player_health += hearts
            self.second_player_health -= attacks
        else:
            # player 2
            self.second_player_points += points
            self.second_player_health += hearts
            self.first_player_health -= attacks

        # you can't get more than 10 health
        if self.first_player_health > 10:
            self.first_player_health = 10
        if self.second_player_health > 10:
            self.second_player_health = 10

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
        game_moves = []
        last_move = self.get_last_move()

        # make a first roll of game, or next players first roll
        if not last_move or last_move.roll == 3: 
            last_move = self.do_move('')

        try:
            show_move = self.move_set.filter(roll=3).order_by('-turn')[:1].get()
        except:
            show_move = None

        if show_move:
            self.append_move(game_moves, show_move)

        if last_move:
            self.append_move(game_moves, last_move)

        return game_moves, last_move.roll

    def append_move(self, moves_list, move_to_append):
        moves_list.append([move_to_append.dice_1,
                           move_to_append.dice_2, 
                           move_to_append.dice_3, 
                           move_to_append.dice_4, 
                           move_to_append.dice_5, 
                           move_to_append.dice_6, 
                           move_to_append.player])

    def get_absolute_url(self):
        return reverse('game_detail', args=[self.id])

    def __unicode__(self):
        return "%s vs %s" % (self.first_player, self.second_player)

class Move(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User, related_name='move_player')
    turn = models.IntegerField()
    roll = models.IntegerField()
    dice_1 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_2 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_3 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_4 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_5 = models.CharField(max_length=1, choices=DICE_CHOICES)
    dice_6 = models.CharField(max_length=1, choices=DICE_CHOICES)
    comment = models.CharField(max_length=300)

    class Meta:
        ordering = ['-turn', '-roll']

    def __unicode__(self):
        return "Game %s, Turn %s" % (self.game, self.turn)


class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_sent")
    to_user = models.ForeignKey(User, related_name="invitations_received",
                                verbose_name="User to invite",
                                help_text="Please select the user you want to play a game with")
    message = models.CharField("Optional Message", max_length=300, blank=True,
                               help_text="Add a message to your invite")
    timestamp = models.DateTimeField(auto_now_add=True)
