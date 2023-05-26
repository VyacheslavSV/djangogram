from pyexpat import model
from rest_framework import serializers

from .models import Post, PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', )


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('author', 'caption', 'created_at', 'images')
