from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
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


# Home Page View
class HomeView(ListView):
    template_name = "index.html"
    model = models.Post
    context_object_name = "posts"
    paginate_by = 10
    queryset = models.Post.objects.select_related("user").all()


class JournalListView(TemplateView):
    template_name = "journals.html"
