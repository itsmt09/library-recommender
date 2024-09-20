from rest_framework import serializers
from books.models import Author, Book, UserFavorite
from django.contrib.auth.models import User

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Book
        fields = '__all__'

class UserFavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ['id', 'book', 'added_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user