from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from .models import Game, Move
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Invitation, Game
from .forms import InvitationForm


def home(request):
    if request.user.is_authenticated():
        first_games, second_games = Game.objects.games_for_user(request.user)
        
        first_waiting_games = first_games.filter(next_to_move=request.user, status='A')
        first_other_games = first_games.exclude(next_to_move=request.user).filter(status='A')
        first_finished_games = first_games.exclude(status='A')
        
        second_waiting_games = second_games.filter(next_to_move=request.user, status='A')
        second_other_games = second_games.exclude(next_to_move=request.user).filter(status='A')
        second_finished_games = second_games.exclude(status='A')
        
        invitations = request.user.invitations_received.all()
        context = {'first_other_games': first_other_games,
                   'first_waiting_games': first_waiting_games,
                   'first_finished_games': first_finished_games,
                   'second_other_games': second_other_games,
                   'second_waiting_games': second_waiting_games,
                   'second_finished_games': second_finished_games,
                   'invitations': invitations}
    else:
        return redirect('login')
    html = render(request, 'home.html', context)
    return HttpResponse(html)


def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.method == 'POST':
        data = request.POST
        game.do_move(data)

    game_moves, last_move_roll = game.as_game()

    html = render(request, 'game_detail.html', {'game': game, 'game_moves': game_moves, 'last_move_roll': last_move_roll})
    return HttpResponse(html)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy('home')


@login_required
def new_invitation(request):
    if request.method == 'POST':
        invitation = Invitation(from_user=request.user)
        form = InvitationForm(data=request.POST, instance=invitation)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = InvitationForm()
    return render(request, "new_invitation.html", {'form': form})


@login_required
def accept_invitation(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)
    if not request.user == invitation.to_user:
        raise PermissionDenied
    if request.method == 'POST':
        if "accept" in request.POST:
            game = Game.objects.new_game(invitation)
            game.save()
            invitation.delete()
            return redirect(game)
        else:
            invitation.delete()
            return redirect('home')
    else:
        return render(request, "accept_invitation.html", {'invitation': invitation})
