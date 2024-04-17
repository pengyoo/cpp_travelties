from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import UserProfile
from .models import DestinationRating
from .models import Destination


# Use django signals to automatically create UserProfile when a user sign up
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# Use signals to calculate average rating when a user rate a property
@receiver(post_save, sender=DestinationRating)
def update_rating(sender, instance, created, **kwargs):
    if created:
        avg_rating = DestinationRating.objects.filter(destination=instance.destination).aggregate(
            avg_rating=Avg('rating'))['avg_rating']
        Destination.objects.filter(
            pk=instance.destination.id).update(rating=avg_rating)
