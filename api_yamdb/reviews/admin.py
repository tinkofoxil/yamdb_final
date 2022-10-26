from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_filter = search_fields = list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    list_filter = search_fields = list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'description',)
    list_filter = ('genre', 'category', 'year',)
    search_fields = ('name', 'year', 'genre', 'category',)
    list_display_links = ('name', 'year',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
