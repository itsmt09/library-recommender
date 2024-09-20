from celery import shared_task
from .recommendation import recommendation_system
from .models import Book
from .serializers import BookSerializer

@shared_task
def generate_recommendations(user_id):
    recommended_books = recommendation_system.recommend(user_id)
    serializer = BookSerializer(recommended_books, many=True)
    return serializer.data