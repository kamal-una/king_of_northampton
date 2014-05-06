from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Invitation, Game, User
from .forms import InvitationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from google.appengine.api import users, channel
import json


def home(request):
    if request.user.is_authenticated():
        first_games, second_games = Game.objects.games_for_user(request.user)
        
        first_waiting_games = first_games.filter(next_to_move=request.user, status='A')
        first_other_games = first_games.exclude(next_to_move=request.user).filter(status='A')
        first_finished_games = first_games.exclude(status='A')
        
        second_waiting_games = second_games.filter(next_to_move=request.user, status='A')
        second_other_games = second_games.exclude(next_to_move=request.user).filter(status='A')
        second_finished_games = second_games.exclude(status='A')

        waiting_games = list(first_other_games) + list(second_other_games)
        other_games = list(first_waiting_games) + list(second_waiting_games)
        finished_games = list(first_finished_games) + list(second_finished_games)
        
        invitations = request.user.invitations_received.all()
        context = {'other_games': waiting_games,
                   'waiting_games': other_games,
                   'finished_games': finished_games,
                   'invitations': invitations}
    else:
        return redirect('login')
    html = render(request, 'home.html', context)
    return HttpResponse(html)


def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    read_move_from_datastore = True

    token = channel.create_channel(str(request.user) + str(game.id))

    if request.method == 'POST':
        data = request.POST
        last_move = game.do_move(data)

        # the datastore doesn't always come back with out latest move!
        # getting the last_move back from do_move means that we don't need to go to the datastore
        if last_move.roll < 3:
            game_moves = []
            game.append_move(game_moves, last_move)
            last_move_roll = last_move.roll
            read_move_from_datastore = False
        else:
            # send message to other player...
            if request.user == game.first_player:
                channel.send_message(str(game.second_player) + str(game.id), '1')
            else:
                channel.send_message(str(game.first_player) + str(game.id), '1')

    if read_move_from_datastore:
        game_moves, last_move_roll = game.as_game()

    context = {'game': game,
               'game_moves': game_moves,
               'last_move_roll': last_move_roll,
               'token': token}

    html = render(request, 'game_detail.html', context)
    return HttpResponse(html)


def my_move(request, pk):
    game = get_object_or_404(Game, pk=pk)
    response_data = {}

    if game.my_move(request.user):
        response_data['mymove'] = 'true'
    else:
        response_data['mymove'] = 'false'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')


def google_signup(request):
    if not request.user.is_authenticated():
        google_user = users.get_current_user()
        if google_user:
            # check the user doesn't already exist
            try:
                find_user = User.objects.get(username=google_user.nickname(),
                                             email=google_user.email())
            except User.DoesNotExist:
                find_user = None

            if not find_user:
                new_user = User.objects.create_user(google_user.nickname(),
                                                    google_user.email(),
                                                    google_user.user_id())
                # stop someone logging in normally into this account
                new_user.is_active = False
                new_user.save()

            new_user = authenticate(username=google_user.nickname(),
                                    email=google_user.email(),
                                    password=google_user.user_id())
            if new_user is not None:
                login(request, new_user)
    return redirect('home')


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
    return render(request, 'new_invitation.html', {'form': form})


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
        return render(request, 'accept_invitation.html', {'invitation': invitation})
