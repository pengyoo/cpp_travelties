import os
import logging
from datetime import datetime
from uuid import uuid4
from django.db import IntegrityError
from django.db.models.query import QuerySet
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
from botocore.exceptions import ClientError

from s3uploader_pilais.s3uploader import upload_file
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

    def get_queryset(self):
        if self.request.user.is_authenticated:
            following_relationship = models.FollowingRelation.objects.filter(
                follower=self.request.user.profile)
            followings = []
            followings.append(self.request.user.profile)
            for f in following_relationship:
                followings.append(f.following)
            return models.Post.objects.select_related("user").filter(user__in=followings)
        else:
            return models.Post.objects.select_related("user").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # following data
            context['journal_count'] = models.Post.objects.filter(
                user=self.request.user.profile).count()
            context['following_count'] = self.request.user.profile.followings.count()
            context['follower_count'] = self.request.user.profile.followers.count()
            context['following_list'] = self.request.user.profile.followings.all(
            ).values_list('following', flat=True)
            context['favor_list'] = self.request.user.profile.favors.all(
            ).values_list('post', flat=True)

            # destination recommendations
            preferences = models.PreferedDestinationType.objects.filter(
                user=self.request.user.profile)
            preference_list = []
            for preference in preferences:
                preference_list.append(preference.prefered_destination_type)
            context['recommendations'] = models.Destination.objects.filter(
                type__in=preference_list)[:10]

        # who to follow
        context['who_to_follow'] = models.UserProfile.objects.all().order_by(
            "-id")[:6]

        return context


# Post (Journal) List View
class PostListView(ListView):
    template_name = "posts.html"
    model = models.Post
    context_object_name = "posts"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_posts'] = models.Post.objects.filter(
            images__isnull=False).order_by("created_at")[:3]
        return context


# Post (Journal) List View
class UserListView(ListView):
    template_name = "users.html"
    model = models.UserProfile
    context_object_name = "users"
    paginate_by = 12

    def get_queryset(self):
        return models.UserProfile.objects.all()
    # .aggregate(
    #         following_count=Count('followings__following'),
    #         follower_count=Count('followings__follower'),
    #         journal_count=Count('posts'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # following data
            context['following_list'] = self.request.user.profile.followings.all(
            ).values_list('following', flat=True)

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
        try:
            image_url = upload_file(image, object_name)
            # Save image object
            image_saved = models.Image.objects.create(
                title=os.path.splitext(image.name)[0], url=image_url)
            # Retuen json data
            data = {"image_id": image_saved.id, "url": image_url}
        except ClientError as e:
            logging.error(e)
            # Retuen json data
            data = {"error": e}

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
class DestinationAllListView(FilterView):
    template_name = "destinations-all.html"
    model = models.Destination
    context_object_name = "destinations"
    paginate_by = 12
    filterset_class = filters.DestinationFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            # destination recommendations
            preferences = models.PreferedDestinationType.objects.filter(
                user=self.request.user.profile)
            preference_list = []
            for preference in preferences:
                preference_list.append(preference.prefered_destination_type)
            context['recommendations'] = models.Destination.objects.filter(
                type__in=preference_list)[:6]

        # Top 10 destinations
        context['top10'] = models.Destination.objects.all().order_by(
            '-rating')[:6]

        # Top 10 destinations
        context['bottom10'] = models.Destination.objects.all().order_by(
            'rating')[:6]

        return context


# Destination List View
class DestinationListView(ListView):
    template_name = "destinations.html"
    context_object_name = "top10"

    # Top 6 popular destinations
    def get_queryset(self):
        return models.Destination.objects.all().order_by(
            '-rating')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            # destination recommendations
            preferences = models.PreferedDestinationType.objects.filter(
                user=self.request.user.profile)
            preference_list = []
            for preference in preferences:
                preference_list.append(preference.prefered_destination_type)
            context['recommendations'] = models.Destination.objects.filter(
                type__in=preference_list)[:6]

        # Bottom 10 destinations
        context['bottom10'] = models.Destination.objects.all().order_by(
            'rating')[:6]

        return context


# Destination Detail View
class DestinationDetailView(DetailView):
    template_name = "destination.html"
    model = models.Destination
    context_object_name = "destination"

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


# Destination Detail View
class MeDetailView(DetailView):
    template_name = "me.html"
    model = User
    context_object_name = "me"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # following data
            context['following_list'] = self.request.user.profile.followings.all(
            ).values_list('following', flat=True)

        return context


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


# Handle Add preference (ajax)
def addPreference(request):
    if request.method == 'POST':
        try:
            models.PreferedDestinationType.objects.create(
                user=request.user.profile, prefered_destination_type=request.POST['preference'])
            data = {"message": "success"}
            return JsonResponse(data)
        except IntegrityError:
            return JsonResponse({"message": "You already add this preference!"})
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Rate a destination (ajax)
def rateDestination(request, destination_id):
    if request.method == 'POST':
        rating = request.POST['rating']
        destination = models.Destination.objects.get(pk=destination_id)
        models.DestinationRating.objects.create(
            user=request.user.profile, destination=destination, rating=rating)
        data = {"message": "success"}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})


# Update a user profile (ajax)
def updateProfile(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            slogan = request.POST['slogan']
            profile = request.POST['profile']
            avatar = request.FILES['avatar']

            if avatar:
                object_name = settings.S3_IMAGE_PATH + \
                    str(uuid4()) + os.path.splitext(avatar.name)[1].lower()
                try:
                    # upload avatar image to S3
                    image_url = upload_file(avatar, object_name)
                    # Save image object
                    image_saved = models.Image.objects.create(
                        title=os.path.splitext(avatar.name)[0], url=image_url)
                    request.user.profile.avatar_image = image_saved
                except ClientError as e:
                    logging.error(e)

            # update profile
            request.user.profile.slogan = slogan
            request.user.profile.profile = profile
            request.user.profile.save()
            
            # response json to client
            data = {"message": "success"}
            return JsonResponse(data)
    else:
        return JsonResponse({"error": "Method is not allowed!"})
