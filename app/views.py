from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
from django_filters.views import FilterView
from django.urls import reverse_lazy

from . import models
from . import forms
from . import filters


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


# Post (Journal) List View
class PostListView(ListView):
    template_name = "posts.html"
    model = models.Post
    context_object_name = "posts"
    paginate_by = 10


# Destination List View
class DestinationListView(FilterView):
    template_name = "destinations.html"
    model = models.Destination
    context_object_name = "destinations"
    paginate_by = 10
    filterset_class = filters.DestinationFilter
