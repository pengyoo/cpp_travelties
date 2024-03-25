from django.contrib import admin
from . import models

admin.site.register(models.Image)
admin.site.register(models.UserProfile)
admin.site.register(models.Post)
admin.site.register(models.Destination)
admin.site.register(models.FollowingRelation)
admin.site.register(models.Comment)
admin.site.register(models.Favor)
