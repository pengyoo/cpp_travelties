from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Avg
from django.conf import settings
import boto3
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


# use signal to send sns message when a user add a destination
@receiver(post_save, sender=Destination)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:

        admin = User.objects.first()
        message = f"Hi, {admin.username}! A new destination {instance.title} added by {instance.user.user.username}, please review it. link: http://x22196242-traveltie-env.eba-xmbmufqa.us-west-2.elasticbeanstalk.com/destinations/{instance.id}"

        # publish message to sns
        sns = boto3.client('sns', 'us-west-2')
        response = sns.publish(
            TopicArn=settings.SNS_TOPIC_ARN,
            Message=message,
            Subject=f"A new destination '{instance.title}' added, please review",
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': admin.email
                }
            }
        )

        # send email to admin
        subscribe_response = sns.subscribe(
            TopicArn=settings.SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=admin.email
        )
