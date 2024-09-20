from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    author_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, blank=True)
    image_url = models.URLField(blank=True)
    about = models.TextField(blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    ratings_count = models.IntegerField(default=0)
    text_reviews_count = models.IntegerField(default=0)
    works_count = models.IntegerField(default=0)
    fans_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Series(models.Model):
    series_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    note = models.TextField(blank=True, null=True)
    series_works_count = models.IntegerField(default=0)
    primary_work_count = models.IntegerField(default=0)
    numbered = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Book(models.Model):
    book_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True)
    isbn13 = models.CharField(max_length=13, blank=True)
    asin = models.CharField(max_length=10, blank=True)
    language = models.CharField(max_length=10, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    rating_dist = models.CharField(max_length=100, blank=True)
    ratings_count = models.IntegerField(default=0)
    text_reviews_count = models.IntegerField(default=0)
    publication_date = models.DateField(null=True, blank=True)
    original_publication_date = models.DateField(null=True, blank=True)
    format = models.CharField(max_length=100, blank=True)
    edition_information = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    num_pages = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.SET_NULL, related_name='books')
    series_position = models.CharField(max_length=10, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    work_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title

class BookList(models.Model):
    list_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True)
    num_pages = models.IntegerField(default=0)
    num_books = models.IntegerField(default=0)
    num_voters = models.IntegerField(default=0)
    created_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list)
    num_likes = models.IntegerField(default=0)
    created_by_name = models.CharField(max_length=255, blank=True)
    created_by_id = models.CharField(max_length=100, blank=True)
    num_comments = models.IntegerField(default=0)
    books = models.ManyToManyField(Book, related_name='book_lists')

    def __str__(self):
        return self.title

class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')