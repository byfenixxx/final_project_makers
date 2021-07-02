from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


MyUser = get_user_model()


class Genre(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=255)
    description = models.TextField()
    book_cover = models.ImageField(upload_to="covers")

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["author", "book"]


class Image(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="posters")
    image = models.ImageField(upload_to="book_images", blank=True, null=True)


class Favorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="favorites")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)
