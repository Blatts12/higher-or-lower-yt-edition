from django import forms


class NewGameForm(forms.Form):
    channel_id = forms.CharField(label="Youtube channel ID", max_length=32)
