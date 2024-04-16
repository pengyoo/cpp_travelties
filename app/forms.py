from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core import validators
from django.contrib.auth.models import User

from . import models


class SignUpForm(UserCreationForm):
    email = forms.EmailField(validators=[validators.validate_email])

    min_length = 5
    max_length = 30
    message_lt_min = f"Should have at least {min_length} characters."
    message_ht_max = f"Should have at most{max_length} characters."

    username = forms.CharField(validators=[validators.MaxLengthValidator(max_length, message_ht_max),
                                           validators.MinLengthValidator(min_length, message_lt_min)])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(forms.ModelForm):

    image_ids = forms.CharField()

    class Meta:
        model = models.Post
        fields = ['title', 'summary', 'content']


class DestinationForm(forms.ModelForm):

    image_ids = forms.CharField()

    class Meta:
        model = models.Destination
        fields = ['title', 'content', 'continent', 'country']


class CommentForm(forms.ModelForm):
    post_id = forms.IntegerField()

    class Meta:
        model = models.Comment
        fields = ['content']
