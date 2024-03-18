from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, CreateView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.contrib.auth.models import User

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


# Create Post (Journal) View
class PostCreateView(CreateView):
    template_name = "index.html"
    model = models.Post
    form_class = forms.PostForm


    def form_valid(self, form):
        form.instance.user = self.request.user
        
        return super().form_valid(form)
    


# Post Detail View
class PostDetailView(DetailView):
    template_name = "post.html"
    model = models.Post
    context_object_name = "post"


# Destination List View
class DestinationListView(FilterView):
    template_name = "destinations.html"
    model = models.Destination
    context_object_name = "destinations"
    paginate_by = 10
    filterset_class = filters.DestinationFilter


# Destination Detail View
class DestinationDetailView(DetailView):
    template_name = "destination.html"
    model = models.Destination
    context_object_name = "destination"


# Destination Detail View
class MeDetailView(DetailView):
    template_name = "me.html"
    model = User
    context_object_name = "me"
