from django.contrib import admin
from .models import User, UserProfile, Post, PostImage, PostTag, PostLike, Tag, CommentTag, Comment, CommentLike
# Register your models here.

admin.site.register(Post)
