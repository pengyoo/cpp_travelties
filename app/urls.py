from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('posts/', views.PostListView.as_view(), name="post_list"),
    path('posts/<int:pk>', views.PostDetailView.as_view(), name="post_detail"),
    path('posts_create/', views.PostCreateView.as_view(), name="post_create"),
    path('image_upload/', views.ImageUploadView, name="image_upload"),
    path('comments_create/', views.CommentCreateView, name="comments_create"),
    path('follow/', views.FollowView, name="follow"),
    path('unfollow/<int:user_id>', views.UnFollowView, name="unfollow"),
    path('favor/', views.FavorView, name="favor"),
    path('unfavor/<int:post_id>', views.UnFavorView, name="unfavor"),
    path('destinations_all/', views.DestinationAllListView.as_view(),
         name="destination_list_all"),
    path('destinations/', views.DestinationListView.as_view(),
         name="destination_list"),
    path('destinations/<int:pk>', views.DestinationDetailView.as_view(),
         name="destination_detail"),
    path('destination_create/', views.DestinationCreateView.as_view(),
         name="destination_create"),

    path('users/', views.UserListView.as_view(), name="user_list"),
    path('me/<int:pk>', views.MeDetailView.as_view(), name="me"),
    path('profile_update/', views.updateProfile, name="profile_update"),

    path('preference_add/', views.addPreference, name="preference_add"),
    path('destination_rate/<int:destination_id>',
         views.rateDestination, name="destination_rate"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', auth_views.LoginView.as_view(template_name='signin.html'), name='signin'),
    path('signout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='signout'),

]
