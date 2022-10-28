from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class RegisterUserSerializer(serializers.ModelSerializer):
    """User model serializer for user registration."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class CategoriesSerializer(serializers.ModelSerializer):
    """Category model serializer."""

    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
        )


class GenresSerializer(serializers.ModelSerializer):
    """Genre model serializer."""

    class Meta:
        model = Genre
        fields = (
            "name",
            "slug",
        )


class ReadTitleSerializer(serializers.ModelSerializer):
    """Title model serializer."""

    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(read_only=True, many=True)
    description = serializers.CharField(required=False)
    rating = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=["name", "year"],
                message="This record has already been created!",
            )
        ]


class CreateTitleSerializer(ReadTitleSerializer):
    """Title model serializer for create operation."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    rating = serializers.IntegerField(required=False)


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer."""

    text = serializers.CharField()
    score = serializers.IntegerField(max_value=10, min_value=1)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "text",
            "author",
            "score",
            "pub_date",
        )
        read_only_fields = (
            "id",
            "title",
            "author",
            "pub_date",
        )


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer."""

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "author",
            "pub_date",
        )
        read_only_fields = (
            "id",
            "author",
            "pub_date",
        )
