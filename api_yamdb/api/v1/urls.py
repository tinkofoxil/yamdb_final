from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriesViewSet,
    CommentViewSet,
    GenresViewSet,
    ManageUsersViewSet,
    PersonalProfileView,
    RegisterUserViewSet,
    RequestJWTView,
    ReviewViewSet,
    TitleViewSet,
)

router = DefaultRouter()
router.register("auth/signup", RegisterUserViewSet)
router.register("users", ManageUsersViewSet)
router.register("categories", CategoriesViewSet, basename="categories")
router.register("genres", GenresViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("auth/token/", RequestJWTView.as_view(), name="request-jwt"),
    path("users/me/", PersonalProfileView.as_view(), name="personal-profile"),
    path("", include(router.urls)),
]
