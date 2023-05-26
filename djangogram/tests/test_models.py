from django.contrib.auth.models import User
from django.test import TestCase

from webapp.models import UserProfile, Post, PostImage, Tag, PostTag, PostLike, Comment, CommentTag, CommentLike, \
    Subscription


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', email='testuser@example.com', password='password')
        self.user2 = User.objects.create(username='user2', email='testuser@example.com', password='password')
        self.user3 = User.objects.create(username='user3', email='testuser@example.com', password='password')
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name='Test User',
            bio='This is a test user',
            avatar='test.jpg')
        self.subscription = Subscription.objects.create(user=self.user, subscribed_to=self.user2)
        self.post = Post.objects.create(
            author=self.user, caption='Test caption')
        self.post_image = PostImage.objects.create(
            post=self.post, image='test.jpg')
        self.tag = Tag.objects.create(name='Test tag')
        self.post_tag = PostTag.objects.create(post=self.post, tag=self.tag)
        self.post_like = PostLike.objects.create(
            post=self.post, user=self.user2)
        self.comment = Comment.objects.create(
            user=self.user2, post=self.post, content='Test comment')
        self.comment_tag = CommentTag.objects.create(
            comment=self.comment, tag=self.tag)
        self.comment_like = CommentLike.objects.create(
            comment=self.comment, user=self.user3)

    def test_user_profile(self):
        self.assertEqual(str(self.profile.user.username), self.user.username)
        self.assertEqual(self.profile.full_name, 'Test User')
        self.assertEqual(self.profile.bio, 'This is a test user')
        self.assertTrue(self.profile.avatar, 'media/avatars/test.jpg')

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.subscribed_to, self.user2)

    def test_post(self):
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.created_at is not None)

    def test_post_image(self):
        self.assertIsInstance(self.post_image, PostImage)
        self.assertEqual(self.post_image.post, self.post)
        self.assertTrue(self.post_image.image, 'media/avatars/test.jpg')

    def test_tag(self):
        self.assertEqual(str(self.tag.name), 'Test tag')
        self.assertEqual(self.tag.name, 'Test tag')

    def test_post_tag(self):
        self.assertEqual(str(self.post_tag), 'PostTag object (1)')
        self.assertEqual(self.post_tag.post, self.post)
        self.assertEqual(self.post_tag.tag, self.tag)

    def test_post_like(self):
        self.assertEqual(str(self.post_like.post), str(self.post))
        self.assertEqual(self.post_like.post, self.post)
        self.assertEqual(self.post_like.user, self.user2)

    def test_comment(self):
        self.assertEqual(str(self.comment), 'Comment object (1)')
        self.assertEqual(self.comment.user, self.user2)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertTrue(self.comment.created_at is not None)

    def test_comment_tag(self):
        self.assertEqual(str(self.comment_tag), 'CommentTag object (1)')
        self.assertEqual(self.comment_tag.comment, self.comment)
        self.assertEqual(self.comment_tag.tag, self.tag)

    def test_comment_like(self):
        self.assertEqual(str(self.comment_like), 'CommentLike object (1)')
        self.assertEqual(self.comment_like.comment, self.comment)
        self.assertEqual(self.comment_like.user, self.user3)
