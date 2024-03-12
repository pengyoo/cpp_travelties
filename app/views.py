from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy

from . import models
from . import forms


# Sign up view: display sign up form and register a user through post request
class SignUpView(CreateView):
    template_name = 'signup.html'
    form_class = forms.SignUpForm
    success_url = reverse_lazy("signin")

    # def form_valid(self, form):
    #     form.send_email()
    #     return super().form_valid(form)


class HomeView(TemplateView):
    template_name = "index.html"


class JournalListView(TemplateView):
    template_name = "journals.html"
