from django.contrib import admin
from . import models


# register Image to admin
@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'sort', 'url', 'type']


# register UserProfile to admin
@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_image', 'profile', 'slogan']


# register Post to admin
@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'summary', 'created_at']


# register Destination to admin
@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at']


# register Comment to admin
@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'user', 'post', 'created_at']


# register Favor to admin
@admin.register(models.Favor)
class FavorAdmin(admin.ModelAdmin):
    list_display = ['user',  'post']


# register Favor to admin
@admin.register(models.FollowingRelation)
class FollowingRelationAdmin(admin.ModelAdmin):
    list_display = ['follower',  'following']
