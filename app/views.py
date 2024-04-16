import os
from datetime import datetime
from uuid import uuid4
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
from django.utils import formats
from django.db.models import Count
from .utils import upload_file
from . import models
from . import forms
from . import filters

LOGIN_URL = '/signin'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['journal_count'] = models.Post.objects.filter(
                user=self.request.user.profile).count()
            context['following_count'] = self.request.user.profile.followings.count()
            context['follower_count'] = self.request.user.profile.followers.count()
            context['following_list'] = self.request.user.profile.followings.all(
            ).values_list('following', flat=True)
            context['favor_list'] = self.request.user.profile.favors.all(
            ).values_list('post', flat=True)

        # who to follow
        context['who_to_follow'] = models.UserProfile.objects.all()[:10]
        return context


# Post (Journal) List View
class PostListView(ListView):
    template_name = "posts.html"
    model = models.Post
    context_object_name = "posts"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_posts'] = models.Post.objects.filter(
            images__isnull=False).order_by("created_at")[:3]
        return context


# Create Post (Journal) View
class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = LOGIN_URL
    template_name = "post-create.html"
    form_class = forms.PostForm

    def form_valid(self, form):
        form.instance.user = self.request.user.profile
        image_ids = form.cleaned_data.get("image_ids").strip().split(",")

        return_value = super().form_valid(form)

        for id in image_ids:
            if id:
                form.instance.images.add(models.Image.objects.get(pk=id))

        return return_value

    # echo form data if data is invalid
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    # redirect to published post
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


# Create Destination View
class DestinationCreateView(LoginRequiredMixin, CreateView):
    login_url = LOGIN_URL
    template_name = "destination-create.html"
    form_class = forms.DestinationForm

    def form_valid(self, form):
        form.instance.user = self.request.user.profile
        image_ids = form.cleaned_data.get("image_ids").strip().split(",")

        return_value = super().form_valid(form)

        for id in image_ids:
            if id:
                form.instance.images.add(models.Image.objects.get(pk=id))

        return return_value

    # echo form data if data is invalid
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    # redirect to published destination
    def get_success_url(self):
        return reverse_lazy('destination_detail', kwargs={'pk': self.object.pk})


# Handle comment create (ajax)
def CommentCreateView(request):
    if request.method == 'POST':

        # Check if user signed in
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthenticated'}, status=403, safe=False)

        form = forms.CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data['post_id']
            content = form.cleaned_data['content']
            post = models.Post.objects.get(pk=post_id)
            comment = models.Comment.objects.create(
                post=post, content=content, user=request.user.profile)
            data = {"comment": comment.content,
                    "username": request.user.username,
                    "user_avatar": request.user.profile.avatar_image.url, "created_at":  formats.date_format(comment.created_at, "DATETIME_FORMAT")}
            return JsonResponse(data)
        else:
            return JsonResponse(form.errors.as_json(), status=300, safe=False)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Handle Image uoload
def ImageUploadView(request):
    if request.method == 'POST':

        # Check if user signed in
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthenticated'}, status=403, safe=False)

        image = request.FILES['image']
        object_name = settings.S3_IMAGE_PATH + \
            str(uuid4()) + os.path.splitext(image.name)[1].lower()
        image_url = upload_file(image, object_name)

        # Save image object
        image_saved = models.Image.objects.create(
            title=os.path.splitext(image.name)[0], url=image_url)

        # Retuen json data
        data = {"image_id": image_saved.id, "url": image_url}

        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Post Detail View
class PostDetailView(DetailView):
    template_name = "post.html"
    model = models.Post
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['journal_count'] = models.Post.objects.filter(
                user=self.request.user.profile).count()
            context['following_count'] = self.request.user.profile.followings.count()
            context['follower_count'] = self.request.user.profile.followers.count()
            context['following_list'] = self.request.user.profile.followings.all(
            ).values_list('following', flat=True)
            context['favor_list'] = self.request.user.profile.favors.all(
            ).values_list('post', flat=True)
        return context


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


# Handle Follow (ajax)
def FollowView(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        following_user = User.objects.prefetch_related('profile').get(
            pk=user_id).profile
        follower_user = request.user.profile
        models.FollowingRelation.objects.get_or_create(
            follower=follower_user, following=following_user)
        data = {"message": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Handle unFollow (ajax)
def UnFollowView(request, user_id):
    if request.method == 'DELETE':
        models.FollowingRelation.objects.filter(
            follower__id=request.user.profile.id, following__id=user_id).delete()
        data = {"message": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Handle favor (ajax)
def FavorView(request):
    if request.method == 'POST':
        post_id = request.POST['post_id']
        user = request.user.profile
        post = models.Post.objects.get(pk=post_id)
        models.Favor.objects.get_or_create(
            post=post, user=user)
        data = {"message": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Handle favor (ajax)
def UnFavorView(request, post_id):
    if request.method == 'DELETE':
        models.Favor.objects.filter(
            user__id=request.user.profile.id, post__id=post_id).delete()
        data = {"message": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})
