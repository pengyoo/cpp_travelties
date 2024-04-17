from django.db import models
from django.contrib.auth.models import User


# Image Model
class Image(models.Model):

    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    sort = models.IntegerField(default=0)

    IMAGE_CHOICES = (
        ('A', 'avatar'),
        ('P', 'post')
    )
    type = models.CharField(max_length=1, choices=IMAGE_CHOICES, default='P')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['sort']


# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    avatar_image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.CharField(max_length=255)
    slogan = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# Prefered Destination Type Model
class PreferedDestinationType(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="preferences")
    prefered_destination_type = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.user.username + ":" + self.prefered_destination_type


# Following Relation Model
class FollowingRelation(models.Model):
    follower = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="followings")
    following = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)


# Post (Journal) Model
class Post(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    images = models.ManyToManyField(Image)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']


# Favor model: map the like relationship between user and post
class Favor(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="favors")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,  related_name="favors")

    def __str__(self):
        return self.user.user.username + " : " + self.post.title


# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]

    class Meta:
        ordering = ['-created_at']


# Destination Model
class Destination(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    images = models.ManyToManyField(Image)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    CONTINENT_CHOICES = (
        ('NA', 'North America'),
        ('SA', 'South America'),
        ('EU', 'Europe'),
        ('AS', 'Asia'),
        ('AF', 'Africa'),
        ('OC', 'Oceania'),
        ('AN', 'Antarctica'),
    )
    continent = models.CharField(max_length=2, choices=CONTINENT_CHOICES)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


# DestinationRating model
class DestinationRating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    rating = models.IntegerField()
