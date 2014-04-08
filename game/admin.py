from django.contrib import admin
from .models import Game, Move, Invitation


class GameAdmin(admin.ModelAdmin):
    list_display = ('first_player', 'second_player', 'next_to_move', 'start_time', 'last_active')


class MoveAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'turn', 'roll', 'dice_1', 'dice_2', 'dice_3', 'dice_4', 'dice_5', 'dice_6', 'comment')


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'message', 'timestamp')


admin.site.register(Game, GameAdmin)
admin.site.register(Move, MoveAdmin)
admin.site.register(Invitation, InvitationAdmin)
