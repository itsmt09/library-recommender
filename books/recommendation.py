from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Book, UserFavorite
from django.db.models import Prefetch

class RecommendationSystem:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.book_vectors = None
        self.book_ids = None

    def fit(self):
        books = Book.objects.all().prefetch_related(
            Prefetch('authors', queryset=Author.objects.only('name'))
        )
        descriptions = []
        self.book_ids = []
        for book in books:
            author_names = ' '.join([author.name for author in book.authors.all()])
            description = f"{book.title} {book.description} {author_names} {book.publisher} {book.genre}"
            descriptions.append(description)
            self.book_ids.append(book.id)
        
        self.book_vectors = self.vectorizer.fit_transform(descriptions)

    def recommend(self, user_id, n=5):
        if not self.book_vectors:
            self.fit()

        user_favorites = UserFavorite.objects.filter(user_id=user_id).select_related('book')
        if not user_favorites:
            return []

        favorite_indices = [self.book_ids.index(fav.book.id) for fav in user_favorites if fav.book.id in self.book_ids]
        favorite_vectors = self.book_vectors[favorite_indices]
        mean_vector = favorite_vectors.mean(axis=0)

        similarities = cosine_similarity(mean_vector, self.book_vectors)
        similar_indices = similarities.argsort()[0][::-1]

        recommended_ids = [
            self.book_ids[i] for i in similar_indices 
            if self.book_ids[i] not in [fav.book.id for fav in user_favorites]
        ][:n]

        return Book.objects.filter(id__in=recommended_ids)

recommendation_system = RecommendationSystem()