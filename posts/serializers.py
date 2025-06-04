# posts/serializers.py
from rest_framework import serializers
from .models import Post, Image, Comment, Like, Location
from django.contrib.auth import get_user_model
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json

User = get_user_model()

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'text', 'created_at']

class LocationSerializer(serializers.ModelSerializer):
    reverse_name = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude', 'reverse_name']

    def get_reverse_name(self, obj):
        geolocator = Nominatim(user_agent="photo_social_app")
        try:
            location = geolocator.reverse((obj.latitude, obj.longitude), timeout=30)
            return location.address if location else None
        except GeocoderTimedOut:
            return None

class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.FileField(max_length=10000000, allow_empty_file=True),
        write_only=True,
        required=False,
        help_text="Можно загрузить несколько файлов, отправляя их под ключом 'images' (например, images[] в Postman или повторные -F images= в curl)"
    )
    location = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    location_data = LocationSerializer(read_only=True, source='location')
    image_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'text', 'created_at', 'images', 'location', 'image_list', 'comments', 'likes_count', 'location_data']

    def get_image_list(self, obj):
        images = obj.images.all()
        return ImageSerializer(images, many=True, context=self.context).data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])  # Извлекаем файлы
        location_json = validated_data.pop('location', None)
        validated_data.pop('author', None)

        post = Post.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        for image_data in images_data:
            Image.objects.create(post=post, image=image_data)

        if location_json:
            try:
                location_data = json.loads(location_json)
                Location.objects.create(
                    post=post,
                    name=location_data.get('name', ''),
                    latitude=location_data.get('latitude', 0.0),
                    longitude=location_data.get('longitude', 0.0)
                )
            except (json.JSONDecodeError, TypeError):
                raise serializers.ValidationError("Invalid location JSON format")

        return post