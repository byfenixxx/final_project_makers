from rest_framework import serializers

from .models import *


class GenreSerializers(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "author", "genre", "title", "description", "book_cover")

    def get_rating(self, instance):
        total_rating = sum(instance.reviews.values_list("rating", flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["reviews"] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation["rating"] = self.get_rating(instance)
        representation["images"] = ImageSerializer(instance.posters.all(), many=True).data
        return representation


class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("email", )

        # def to_representation(self, instance):
        #     representation = super().to_representation(instance)
        #     if not instance.email:
        #         representation["email"] = "Анонимный пользователь"
        #     return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ("id", "author")

    def validate_book(self, product):
        request = self.context.get("request")
        if product.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError("Вы не можете добавить отзыв")
        return product

    def validate_rating(self, rating):
        if rating not in range(1, 6):
            raise serializers.ValidationError("Ретинг должен быть о 1 до 5")
        return rating

    def validate(self, attrs):
        request = self.context.get("request")
        attrs["author"] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["author"] = ReviewAuthorSerializer(instance.author).data
        return rep


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image", "book"]

    def to_representation(self, instance):
        representation = super(ImageSerializer, self).to_representation(instance)
        del representation["book"]
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ["user", "book"]

    def to_representation(self, instance):
        representation = super(FavoriteSerializer, self).to_representation(instance)
        del representation["user"]
        representation["book"] = instance.book.title

        return representation

