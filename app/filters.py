import django_filters
from . import models


# Destination filter
class DestinationFilter(django_filters.FilterSet):

    class Meta:
        model = models.Destination
        fields = {
            'continent': ['exact'],
            'country': ['contains'],
            'city': ['contains'],
            'title': ['contains']
        }
