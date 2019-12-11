from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("register", views.register),
    path("login", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout", auth_views.LogoutView.as_view()),
    path("", RedirectView.as_view(url="/posts"), name="home"),
    path("posts", views.PostListView.as_view()),
    path("posts/<str:post_id>", views.PostDetailView.as_view()),
    path("users", views.UserListView.as_view()),
    path("managers", views.AdminView.as_view()),
]
