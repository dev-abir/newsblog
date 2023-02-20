from django.urls import path, include

from .views import (
    index,
    UserCreateView,
    login_view,
    logout_view,
    UserDetailView,
    BlogListView,
    BlogDetailView,
    BlogCreateView,
    BlogDeleteView,
    BlogUpdateView,
    BlogViewSet,
)

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"blogs", BlogViewSet, basename="blogs-api")

urlpatterns = [
    path("", index, name="index"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("blogs/", BlogListView.as_view(), name="blog-list"),
    path("blogs/add/", BlogCreateView.as_view(), name="blog-create"),
    path("blogs/<slug:slug>/", BlogDetailView.as_view(), name="blog-detail"),
    path("blogs/<slug:slug>/update/", BlogUpdateView.as_view(), name="blog-update"),
    path("blogs/<slug:slug>/delete/", BlogDeleteView.as_view(), name="blog-delete"),
    path("api/", include(router.urls)),
]
