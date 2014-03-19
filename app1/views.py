from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Game, Move

# Create your views here.
def home(request):
    if request.user.is_authenticated():
        user_games = Game.objects.games_for_user(request.user)
        waiting_games = user_games.filter(next_to_move=request.user, status='A')
        other_games = user_games.exclude(next_to_move=request.user).filter(status='A')
        finished_games = user_games.exclude(status='A')
        context = {'other_games': other_games,
                    'waiting_games': waiting_games,
                    'finished_games': finished_games}
    else:
        context = ''
    html = render(request, 'home.html', context)
    return HttpResponse(html)


def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)

    context = {'game': game}
    if request.method == 'POST':
        data = request.POST
        game.do_move(data)

    html = render(request, 'game_detail.html', {'game': game})
    return HttpResponse(html)