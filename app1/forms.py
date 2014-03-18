from django.forms import ModelForm
from .models import Move
from django.core.exceptions import ValidationError

class MoveForm(ModelForm):
    class Meta:
        model = Move
        exclude = ('game', 'by_first_player', 'comment')

    def clean(self):
        game = self.instance.game
        hold1 = self.cleaned_data.get("hold1")
        hold2 = self.cleaned_data.get("hold2")
        hold3 = self.cleaned_data.get("hold3")
        hold4 = self.cleaned_data.get("hold4")
        hold5 = self.cleaned_data.get("hold5")
        hold6 = self.cleaned_data.get("hold6")
        if not game or not game.status == "A" or not game.is_empty(hold1, hold2, hold3, hold4, hold5, hold6):
            raise ValidationError("Illegal move")
        return self.cleaned_data