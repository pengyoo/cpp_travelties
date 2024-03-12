from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('posts/', views.PostListView.as_view(), name="post_list"),
    path('post/<int:pk>', views.PostDetailView.as_view(), name="post_detail"),
    path('destinations/', views.DestinationListView.as_view(),
         name="destination_list"),

    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', auth_views.LoginView.as_view(template_name='signin.html'), name='signin'),
    path('signout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='signout'),

]
