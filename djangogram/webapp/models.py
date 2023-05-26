from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    avatar = CloudinaryField(getattr(settings, 'CLOUDINARY_AVATAR_FOLDER'), blank=True)
    subscriptions = models.ManyToManyField(User, blank=True, related_name='user_subscriptions')


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscribers')
    created_at = models.DateTimeField(auto_now_add=True)


class PostManager(models.Manager):
    def get_feed_posts(self, user):
        subscriptions = user.profile.subscriptions.all()
        return Post.objects.filter(author__in=subscriptions).order_by('-created_at')


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = PostManager()


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField(getattr(settings, 'CLOUDINARY_MEDIA_FOLDER'), blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=255)


class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='posts')


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class CommentTag(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='comments')


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
