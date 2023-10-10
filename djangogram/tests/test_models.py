from django.contrib.auth.models import User
from django.test import TestCase

from webapp.models import UserProfile, Post, PostImage, Tag, PostTag, PostLike, Comment, CommentTag, CommentLike, \
    Subscription


class ModelTests(TestCase):
    def setUp(self):
        """
        Set up the initial state for the test case.
        This function creates various objects such as users,
        user profiles, subscriptions, posts, post images, tags, comments, etc.
        to set up the initial state for the test case.
        """
        self.user = User.objects.create(username='user', email='testuser@example.com', password='password')
        self.user2 = User.objects.create(username='user2', email='testuser@example.com', password='password')
        self.user3 = User.objects.create(username='user3', email='testuser@example.com', password='password')
        self.profile = UserProfile.objects.create(user=self.user, full_name='Test User', bio='This is a test user',
                                                  avatar='test.jpg')
        self.subscription = Subscription.objects.create(user=self.user, subscribed_to=self.user2)
        self.post = Post.objects.create(author=self.user, caption='Test caption')
        self.post_image = PostImage.objects.create(post=self.post, image='test.jpg')
        self.tag = Tag.objects.create(name='Test tag')
        self.post_tag = PostTag.objects.create(post=self.post, tag=self.tag)
        self.post_like = PostLike.objects.create(post=self.post, user=self.user2)
        self.comment = Comment.objects.create(user=self.user2, post=self.post, content='Test comment')
        self.comment_tag = CommentTag.objects.create(comment=self.comment, tag=self.tag)
        self.comment_like = CommentLike.objects.create(comment=self.comment, user=self.user3)

    def test_user_profile(self):
        """
        Test the user profile.
        Asserts:
            - The username of the profile user is equal to the username of the user.
            - The full name of the profile is 'Test User'.
            - The bio of the profile is 'This is a test user'.
            - The avatar of the profile is 'media/avatars/test.jpg'.
        """
        self.assertEqual(str(self.profile.user.username), self.user.username)
        self.assertEqual(self.profile.full_name, 'Test User')
        self.assertEqual(self.profile.bio, 'This is a test user')
        self.assertTrue(self.profile.avatar, 'media/avatars/test.jpg')

    def test_subscription_creation(self):
        """
        Test the creation of a subscription.
        Asserts that the user attribute of the subscription is equal to the self.user attribute.
        Asserts that the subscribed_to attribute of the subscription is equal to the self.user2 attribute.
        """
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.subscribed_to, self.user2)

    def test_post(self):
        """
        Test the 'post' method of the class.
        Asserts that the 'post' attribute is an instance of the 'Post' class.
        Asserts that the 'author' attribute of the 'post' object is equal to the 'user' attribute.
        Asserts that the 'created_at' attribute of the 'post' object is not None.
        """
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.created_at is not None)

    def test_post_image(self):
        """
        Test the `post_image` attribute of the class.
        This function asserts that the `post_image` attribute is an instance of the `PostImage` class,
        that its `post` attribute is equal to the `post` attribute of the class,
        and that the `image` attribute is truthy and equal to the string 'media/avatars/test.jpg'.
        """
        self.assertIsInstance(self.post_image, PostImage)
        self.assertEqual(self.post_image.post, self.post)
        self.assertTrue(self.post_image.image, 'media/avatars/test.jpg')

    def test_tag(self):
        """
        Test the tag name by asserting it with a string representation and directly comparing it.
        This function does not take any parameters.
        This function does not return anything.
        """
        self.assertEqual(str(self.tag.name), 'Test tag')
        self.assertEqual(self.tag.name, 'Test tag')

    def test_post_tag(self):
        """
        A test case to verify the functionality of the `test_post_tag` method.
        This method checks whether the `PostTag` object is created correctly,
        and whether it has the expected post and tag attributes.
        """
        self.assertEqual(str(self.post_tag), 'PostTag object (1)')
        self.assertEqual(self.post_tag.post, self.post)
        self.assertEqual(self.post_tag.tag, self.tag)

    def test_post_like(self):
        """
        Test the post_like function.
        Asserts that the post_like's post attribute is equal to the given post
        and the post_like's user attribute is equal to the given user.
        """
        self.assertEqual(str(self.post_like.post), str(self.post))
        self.assertEqual(self.post_like.post, self.post)
        self.assertEqual(self.post_like.user, self.user2)

    def test_comment(self):
        """
        Test the functionality of the `comment` method.
        Test if the `str` method of the `Comment` object returns the correct value.
        Test if the `user` attribute of the `Comment` object is set correctly.
        Test if the `post` attribute of the `Comment` object is set correctly.
        Test if the `content` attribute of the `Comment` object is set correctly.
        Test if the `created_at` attribute of the `Comment` object is not None.
        """
        self.assertEqual(str(self.comment), 'Comment object (1)')
        self.assertEqual(self.comment.user, self.user2)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertTrue(self.comment.created_at is not None)

    def test_comment_tag(self):
        """
        A test function to check the properties of the CommentTag object.
        This function asserts that the string representation of the CommentTag object is 'CommentTag object (1)'.
        It also asserts that the comment property of the CommentTag object is equal to the comment attribute passed to the function.
        Finally, it asserts that the tag property of the CommentTag object is equal to the tag attribute passed to the function.
        """
        self.assertEqual(str(self.comment_tag), 'CommentTag object (1)')
        self.assertEqual(self.comment_tag.comment, self.comment)
        self.assertEqual(self.comment_tag.tag, self.tag)

    def test_comment_like(self):
        """
        Test the functionality of the `comment_like` method.
        Asserts that the string representation of the `comment_like` object is equal to 'CommentLike object (1)'.
        Asserts that the `comment` attribute of the `comment_like` object is equal to the `comment` attribute of the test instance.
        Asserts that the `user` attribute of the `comment_like` object is equal to the `user3` attribute of the test instance.
        """
        self.assertEqual(str(self.comment_like), 'CommentLike object (1)')
        self.assertEqual(self.comment_like.comment, self.comment)
        self.assertEqual(self.comment_like.user, self.user3)
