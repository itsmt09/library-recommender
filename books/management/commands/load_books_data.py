import json
from django.core.management.base import BaseCommand
from books.models import Author, Series, Book, BookList
from django.db import transaction
from django.utils.dateparse import parse_date
from datetime import datetime

class Command(BaseCommand):
    help = 'Load books data from JSON files'

    def handle(self, *args, **options):
        self.load_authors()
        self.load_series()
        self.load_books()
        self.load_lists()

    @transaction.atomic
    def load_authors(self):
        with open('/kaggle/input/large-books-metadata-dataset-50-mill-entries/authors.json/authors.json', 'r') as file:
            authors_data = json.load(file)
            for author_data in authors_data:
                Author.objects.create(
                    author_id=author_data['id'],
                    name=author_data['name'],
                    gender=author_data.get('gender', ''),
                    image_url=author_data.get('image_url', ''),
                    about=author_data.get('about', ''),
                    average_rating=author_data.get('average_rating'),
                    ratings_count=author_data.get('ratings_count', 0),
                    text_reviews_count=author_data.get('text_reviews_count', 0),
                    works_count=author_data.get('works_count', 0),
                    fans_count=author_data.get('fans_count', 0)
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded authors'))

    @transaction.atomic
    def load_series(self):
        with open('/kaggle/input/large-books-metadata-dataset-50-mill-entries/series.json/series.json', 'r') as file:
            series_data = json.load(file)
            for series_item in series_data:
                Series.objects.create(
                    series_id=series_item['id'],
                    title=series_item['title'],
                    description=series_item.get('description', ''),
                    note=series_item.get('note'),
                    series_works_count=int(series_item.get('series_works_count', 0)),
                    primary_work_count=int(series_item.get('primary_work_count', 0)),
                    numbered=series_item.get('numbered', 'false').lower() == 'true'
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded series'))

    @transaction.atomic
    def load_books(self):
        with open('/kaggle/input/large-books-metadata-dataset-50-mill-entries/books.json/books.json', 'r') as file:
            books_data = json.load(file)
            for book_data in books_data:
                book = Book.objects.create(
                    book_id=book_data['id'],
                    title=book_data['title'],
                    isbn=book_data.get('isbn', ''),
                    isbn13=book_data.get('isbn13', ''),
                    asin=book_data.get('asin', ''),
                    language=book_data.get('language', ''),
                    average_rating=book_data.get('average_rating'),
                    rating_dist=book_data.get('rating_dist', ''),
                    ratings_count=book_data.get('ratings_count', 0),
                    text_reviews_count=book_data.get('text_reviews_count', 0),
                    publication_date=parse_date(book_data.get('publication_date')),
                    original_publication_date=parse_date(book_data.get('original_publication_date')),
                    format=book_data.get('format', ''),
                    edition_information=book_data.get('edition_information', ''),
                    image_url=book_data.get('image_url', ''),
                    publisher=book_data.get('publisher', ''),
                    num_pages=book_data.get('num_pages'),
                    description=book_data.get('description', ''),
                    series_position=book_data.get('series_position', ''),
                    work_id=book_data.get('work_id', '')
                )
                
                # Add authors
                for author_data in book_data.get('authors', []):
                    author, _ = Author.objects.get_or_create(author_id=author_data['id'])
                    book.authors.add(author)
                
                # Add series if exists
                if 'series_id' in book_data:
                    series, _ = Series.objects.get_or_create(series_id=book_data['series_id'])
                    book.series = series
                    book.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded books'))

    @transaction.atomic
    def load_lists(self):
        with open('/kaggle/input/large-books-metadata-dataset-50-mill-entries/list.json/list.json', 'r') as file:
            lists_data = json.load(file)
            for list_data in lists_data:
                book_list = BookList.objects.create(
                    list_id=list_data['id'],
                    title=list_data['title'],
                    description=list_data['description'],
                    description_html=list_data['description_html'],
                    num_pages=list_data['num_pages'],
                    num_books=list_data['num_books'],
                    num_voters=list_data['num_voters'],
                    created_date=datetime.strptime(list_data['created_date'], '%B %d, %Y').date(),
                    tags=list_data['tags'],
                    num_likes=list_data['num_likes'],
                    created_by_name=list_data['created_by']['name'],
                    created_by_id=list_data['created_by']['id'],
                    num_comments=list_data['num_comments']
                )
                
                # Add books to the list
                for book_data in list_data.get('books', []):
                    book, _ = Book.objects.get_or_create(book_id=book_data['id'])
                    book_list.books.add(book)

        self.stdout.write(self.style.SUCCESS('Successfully loaded book lists'))