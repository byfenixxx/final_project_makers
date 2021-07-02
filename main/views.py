from django.contrib.auth import get_user_model
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny

from .filters import BookFilter
from .models import Genre, Book, Review, Image, Favorite
from .serializers import GenreSerializers, BookSerializer, ReviewSerializer, ImageSerializer, FavoriteSerializer


User = get_user_model()


class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializers
    permission_classes = [AllowAny, ]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = BookFilter

    def get_permissions(self):
        """Переопределяем метод"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permissions = [IsAdminUser, ]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]

    @action(detail=True, methods=["POST"])
    def create_review(self, request, pk):
        data = request.data.copy()
        data["book"] = pk
        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=["get"])  # router builds path posts/search/?q=paris
    def search(self, request, pk=None):
        q = request.query_params.get("q")  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def add_to_favorite(self, request, pk):
        book = self.get_object()
        user = request.user
        like_obj, created = Favorite.objects.get_or_create(book=book, user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response("disliked")
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response("liked")

    @action(detail=False, methods=["get"])
    def favorites(self, request, pk=None):
        user = request.user
        queryset = user.favorites.all()
        queryset = queryset.filter(user=request.user)
        serializer = FavoriteSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class ImageView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
