from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Author, Book, UserFavorite
from .serializers import AuthorSerializer, BookSerializer, UserSerializer, UserFavoriteSerializer
from django.shortcuts import get_object_or_404
from .recommendation import recommendation_system
from django.core.cache import cache
from rest_framework.decorators import action

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related('book')

    def perform_create(self, serializer):
        if UserFavorite.objects.filter(user=self.request.user).count() >= 20:
            return Response({"error": "Maximum number of favorites reached"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=False, methods=['GET'])
    def recommendations(self, request):
        task = generate_recommendations.delay(request.user.id)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['GET'])
    def recommendation_status(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "No task_id provided"}, status=status.HTTP_400_BAD_REQUEST)

        task_result = AsyncResult(task_id)
        if task_result.ready():
            result = task_result.get()
            return Response(result)
        else:
            return Response({"status": "Processing"}, status=status.HTTP_202_ACCEPTED)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__name']

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        book = self.get_object()
        if request.method == 'POST':
            if UserFavorite.objects.filter(user=request.user).count() >= 20:
                return Response({"error": "Maximum number of favorites reached"}, status=status.HTTP_400_BAD_REQUEST)
            UserFavorite.objects.get_or_create(user=request.user, book=book)
            cache.delete(f'user_{request.user.id}_recommendations')
            return Response({"message": "Book added to favorites"}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            UserFavorite.objects.filter(user=request.user, book=book).delete()
            cache.delete(f'user_{request.user.id}_recommendations')
            return Response({"message": "Book removed from favorites"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)