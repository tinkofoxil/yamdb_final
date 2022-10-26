from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.tokens import confirmation_code

from .filters import TitleFilter
from .permissions import (
    AccessPersonalProfileData,
    AdminUserOnly,
    AllowPostForAnonymousUser,
    ReviewCommentPermission,
    TitleGenreCategoryPermission,
)
from .serializers import (
    CategoriesSerializer,
    CommentSerializer,
    CreateTitleSerializer,
    GenresSerializer,
    ReadTitleSerializer,
    RegisterUserSerializer,
    ReviewSerializer,
    UserSerializer,
)

User = get_user_model()


def check_required_fields(request, field_names):
    """Check required fields and return errors or None."""
    errors = {}
    for field_name in field_names:
        if not request.data.get(field_name):
            errors[field_name] = ["This field is required."]
    if len(errors) > 0:
        return errors


class RegisterUserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """New user registration view."""

    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowPostForAnonymousUser,)

    def perform_create(self, serializer):
        """Create confirmation code, save and send email."""
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        # Create confirmation code and save user
        user = User(username=username)
        token = confirmation_code.make_token(user)
        serializer.save(confirmation_code=token)
        # Send email with confirmation code
        send_mail(
            subject=settings.CONFIRMATION_SUBJECT,
            message=settings.CONFIRMATION_MESSAGE.format(token),
            from_email=settings.SIGNUP_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        """Override response status to 200_OK."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class RequestJWTView(views.APIView):
    """Request JWT token view."""

    permission_classes = (AllowPostForAnonymousUser,)

    def post(self, request):
        # Check required fields
        required_fields = ["username", "confirmation_code"]
        errors = check_required_fields(request, required_fields)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        # Get user from db and check confirmation code
        user = get_object_or_404(User, username=request.data.get("username"))
        if user.confirmation_code != request.data.get("confirmation_code"):
            return Response(
                {"confirmation_code": ["Does not match."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({"token": str(refresh.access_token)})


class ManageUsersViewSet(viewsets.ModelViewSet):
    """Manage users view."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    permission_classes = (AdminUserOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("username",)
    ordering = ("username",)


class PersonalProfileView(views.APIView):
    """Read and edit personal profile data view."""

    permission_classes = (AccessPersonalProfileData,)

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = get_object_or_404(User, username=request.user.username)
        # Do not allow user to change his role
        data = request.data.dict()
        if request.data.get("role"):
            data["role"] = user.role
        serializer = UserSerializer(user, data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseCreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Custom base class for Categories and Genres."""

    permission_classes = (TitleGenreCategoryPermission,)
    lookup_field = "slug"
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("=name",)
    ordering = ("name",)


class CategoriesViewSet(BaseCreateListDestroyViewSet):
    """Category viewset."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(BaseCreateListDestroyViewSet):
    """Genre viewset."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Title viewset."""

    queryset = Title.objects.annotate(rating=Avg("reviews__score")).all()
    permission_classes = (TitleGenreCategoryPermission,)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_class = TitleFilter
    search_fields = ("=name",)
    ordering = ("name",)

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadTitleSerializer
        return CreateTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Review viewset."""

    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermission,)

    def get_title_or_404(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title_or_404().reviews.all()

    def perform_create(self, serializer):
        try:
            serializer.save(
                author=self.request.user, title=self.get_title_or_404()
            )
        except IntegrityError:
            raise ParseError(
                detail={"Integrity error": "This review already exists"}
            )


class CommentViewSet(viewsets.ModelViewSet):
    """Comment viewset."""

    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermission,)

    def get_review_or_404(self):
        return get_object_or_404(
            Review,
            title=self.kwargs.get("title_id"),
            id=self.kwargs.get("review_id"),
        )

    def get_queryset(self):
        return self.get_review_or_404().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, review=self.get_review_or_404()
        )
