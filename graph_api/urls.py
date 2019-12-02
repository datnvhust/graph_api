from django.urls import path
from . import views
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login", auth_views.LoginView.as_view(template_name="adminlte/login.html")),
    path("logout", auth_views.LogoutView.as_view()),
    path("", RedirectView.as_view(url="/posts")),
    path("posts", views.PostListView.as_view()),
    path("posts/<str:post_id>", views.PostDetailView.as_view()),
    path("users", views.UserListView.as_view()),
]
