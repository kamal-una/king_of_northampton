from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


from .models import Game

# Create your views here.
def home(request):
    if request.user.is_authenticated():
        user_games = Game.objects.games_for_user(request.user)
        #active_games = user_games.filter(status='A')
        finished_games = user_games.exclude(status='A')
        waiting_games = user_games.filter(next_to_move=request.user)
        other_games = user_games.exclude(next_to_move=request.user)
        context = {'other_games': other_games,
                    'waiting_games': waiting_games,
                    'finished_games': finished_games}
    else:
        context = ''
    html = render(request, 'home.html', context)
    return HttpResponse(html)


def game_detail(request, pk):
    print pk
    game = get_object_or_404(Game, pk=pk)
    html = render(request, 'game_detail.html', {'game': game})
    return HttpResponse(html)