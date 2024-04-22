from django.contrib import admin
from django.utils.html import format_html
from . import models


admin.site.register(models.PreferedDestinationType)

# register Image to admin


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'title', 'description', 'sort', 'type']

    def image(self, image):
        """ display image """
        return format_html('<img src="{}" class="thumbnail"/>',
                           image.url)

    class Media:
        """ load style files """
        css = {
            'all': ['app/css/styles.css']
        }


# register UserProfile to admin
@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'iamge', 'profile', 'slogan']

    def iamge(self, profile):
        """ display image """
        return format_html('<img src="{}" class="avatar_thumbnail"/>',
                           profile.avatar_image.url)

    class Media:
        """ load style files """
        css = {
            'all': ['app/css/styles.css']
        }


# register Post to admin
@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'summary', 'created_at', 'cover_image']

    def cover_image(self, post):
        """ display image """
        return format_html('<img src="{}" class="thumbnail"/>',
                           post.images.first().url)

    class Media:
        """ load style files """
        css = {
            'all': ['app/css/styles.css']
        }


# register Destination to admin
@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'iamge']

    def iamge(self, destination):
        """ display image """
        return format_html('<img src="{}" class="thumbnail"/>',
                           destination.images.first().url)

    class Media:
        """ load style files """
        css = {
            'all': ['app/css/styles.css']
        }


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
