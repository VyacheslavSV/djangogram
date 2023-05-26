import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from webapp.forms import RegisterForm, LoginForm, PostForm, CommentForm, PostImageForm, BioForm, PostTagForm
from webapp.models import Post, Comment, Tag, UserProfile, PostTag, CommentTag, PostImage, Subscription


class TestSignUpView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('register')
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@example.com',
                                             password='testpassword123')

    def test_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/register.html')
        self.assertTrue(isinstance(response.context['form'], RegisterForm))

    def test_post_valid(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)


class TestSignInView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123')

    def test_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/login.html')
        self.assertTrue(isinstance(response.context['form'], LoginForm))

    def test_post_valid(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('posts'))


class TestSingOutView(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123')

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)


class TestSubscribeView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(
            user=self.user, full_name='Test User')
        self.user_to_subscribe = User.objects.create_user(
            username='testuser2', password='testpass2')
        self.url = reverse('subscribe', args=[self.user_to_subscribe.id])

    def test_subscribe_post_successfully(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn('is_subscribed', data)
        self.assertEqual(data['is_subscribed'], True)
        self.assertTrue(self.user.profile.subscriptions.filter(id=self.user_to_subscribe.id).exists())
        self.assertTrue(Subscription.objects.filter(user=self.user, subscribed_to=self.user_to_subscribe).exists())


class TestFeedViewCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(
            user=self.user, full_name='Test User')

    def test_feed_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/feed.html')
        self.assertQuerysetEqual(response.context['posts'], [])
        post1 = Post.objects.create(author=self.user, caption='Post 1')
        post2 = Post.objects.create(author=self.user, caption='Post 2')

        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(caption='Test Post', author=self.user)

    def test_home_view(self):
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/home.html')
        self.assertContains(response, 'Test Post')

    def test_home_view_with_no_login(self):
        self.client.logout()
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=%2F')


class TestLikePostView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.post = Post.objects.create(caption='Test Post', author=self.user)

    def test_like_post(self):
        client = Client()
        client.login(username='testuser', password='password123')
        response = client.post(reverse('like-post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn('is_liked', data)
        self.assertEqual(data['is_liked'], True)
        self.assertIn('likes_count', data)
        self.assertEqual(data['likes_count'], 1)
        self.assertEqual(self.post.likes.count(), 1)


class TestLikeCommentView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.post = Post.objects.create(caption='Test Post', author=self.user)
        self.comment = Comment.objects.create(
            post=self.post, user=self.user, content='This is a test comment.')

    def test_like_comment(self):
        client = Client()
        client.login(username='testuser', password='password123')
        response = client.post(reverse('like-comment', args=[self.post.id, self.comment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn('is_liked', data)
        self.assertEqual(data['is_liked'], True)
        self.assertIn('likes_count', data)
        self.assertEqual(data['likes_count'], 1)
        self.assertEqual(self.comment.likes.count(), 1)


class TestUserBioView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
        self.url = reverse('user-information')

    def test_get_with_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/user_info.html')
        self.assertContains(response, 'Test bio')

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_get_with_no_bio(self):
        self.client.login(username='testuser', password='testpass')
        self.user_profile.delete()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user-bio-create'))


class TestUserBioCreateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.url = reverse('user-bio-create')

    def test_get_with_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')
        self.assertIsInstance(response.context['form'], BioForm)

    def test_get_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_post_with_valid_data(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'full_name': 'testuser',
            'bio': 'New test bio'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('user-information'))
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            UserProfile.objects.get(
                user=self.user).bio,
            'New test bio')

    def test_post_with_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        data = {
            'bio': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')
        self.assertIsInstance(response.context['form'], BioForm)
        self.assertContains(response, 'Please correct the following errors:')


class TestUserBioEditView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.userprofile = UserProfile.objects.create(
            user=self.user, bio='This is a test bio')
        self.url = reverse('user-edit', args=[self.userprofile.id])
        self.data = {'full_name': 'testuser', 'bio': 'This is a test bio edit'}

    def test_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')

    def test_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-information'))
        self.userprofile.refresh_from_db()
        self.assertEqual(self.userprofile.bio, 'This is a test bio edit')


class TestCreatePostView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('post-create')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/post_form.html')
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsInstance(
            response.context['post_image_form'],
            PostImageForm)
        self.assertIsInstance(response.context['tag_form'], PostTagForm)

    def test_post_valid_form(self):
        data = {'caption': 'Test post',
                'images-0-image': SimpleUploadedFile("test_image.jpg",
                                                     b"file_content",
                                                     content_type="image/jpeg"),
                'name': 'test1, test2',
                }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(PostImage.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(PostTag.objects.count(), 2)


class TestEditPostView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.post = Post.objects.create(
            author=self.user,
            caption='Test caption'
        )
        self.url = reverse('post-edit', args=[self.post.pk])

    def test_get_edit_post_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/post_form.html')
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsInstance(
            response.context['post_image_form'],
            PostImageForm)
        self.assertIsInstance(response.context['tag_form'], PostTagForm)
        self.assertQuerysetEqual(
            response.context['post_tags'],
            self.post.tags.all(),
            transform=lambda x: x)

    def test_post_edit_post_view(self):
        self.client.login(username='testuser', password='testpass')
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg")
        data = {
            'caption': 'New test caption',
            'avatar': image_file,
            'name': 'tag1, tag2'
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.caption, 'New test caption')
        self.assertIsNotNone(self.post.images.first())


class TestDeletePostView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='Test post')

    def test_authenticated_user_can_access_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('post-delete', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_view(self):
        response = self.client.get(reverse('post-delete', args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/accounts/login/?next=/posts/delete/1/')

    def test_post_successfully_deleted_from_database(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('post-delete', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(pk=self.post.id).exists())


class TestAllCommentsForPostView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, caption='Test post', )
        self.comment = Comment.objects.create(
            user=self.user, post=self.post, content='Test comment')
        self.url = reverse('all-comments-for-post', args=[self.post.pk])

    def test_get_comments_for_valid_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/comments_post.html')

    def test_multiple_comments_for_post(self):
        self.client.login(username='testuser', password='testpass')
        comment1 = Comment.objects.create(
            user=self.user, post=self.post, content='Test comment 1')
        comment2 = Comment.objects.create(
            user=self.user, post=self.post, content='Test comment 2')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(comment1, response.context['comments'])
        self.assertIn(comment2, response.context['comments'])

    def test_invalid_post_id(self):
        response = self.client.get('/comments/999/')
        self.assertEqual(response.status_code, 404)

    def test_rendering_template(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'webapp/comments_post.html')

    def test_context_contains_correct_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.context['post'], self.post)
        self.assertIn(self.comment, response.context['comments'])


class TestCommentsForPostCreateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, caption='test caption', )
        self.url = reverse('comments-create', args=[self.post.pk])

    def test_comment_creation_success(self):
        # Test that a comment is created successfully with valid comment and
        # tag forms
        self.client.force_login(self.post.author)
        response = self.client.post(
            self.url, {
                'content': 'test comment', 'name': 'tag1, tag2'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 2)
        self.assertEqual(len(CommentTag.objects.all()), 2)

    def test_comment_creation_success_empty_tag(self):
        # Test that a comment is created successfully with valid comment form
        # and empty tag form
        self.client.force_login(self.post.author)
        response = self.client.post(
            self.url, {'content': 'test comment', 'name': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 0)
        self.assertEqual(len(CommentTag.objects.all()), 0)

    def test_comment_creation_failure_invalid_form(self):
        # Test that an error message is displayed when the comment form is
        # invalid
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the following errors:')
        self.assertEqual(len(Comment.objects.all()), 0)
        self.assertEqual(len(Tag.objects.all()), 0)
        self.assertEqual(len(CommentTag.objects.all()), 0)

    def test_comment_creation_failure_duplicate_tags(self):
        # Test that only unique tags are created when the tag form contains
        # duplicate tags
        self.client.force_login(self.post.author)
        response = self.client.post(
            self.url, {
                'content': 'test comment', 'name': 'tag1, tag1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 1)
        self.assertEqual(len(CommentTag.objects.all()), 2)

    def test_comment_creation_success_invalid_tag(self):
        # Test that a comment is created successfully with valid comment form
        # and invalid tag form
        self.client.force_login(self.post.author)
        response = self.client.post(
            self.url, {
                'content': 'test comment', 'name': 'tag1, , tag2'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 3)
        self.assertEqual(len(CommentTag.objects.all()), 3)


class TestEditCommentView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, caption='test caption', )
        self.comment = Comment.objects.create(
            user=self.user, post=self.post, content='Test Comment')
        self.data = {'user': self.user,
                     'post': self.post,
                     'caption': 'Test post',
                     'images-0-image': SimpleUploadedFile("test_image.jpg",
                                                          b"file_content",
                                                          content_type="image/jpeg"),
                     'content': 'Updated Comment',
                     'name': 'test1, test2',
                     }
        self.url = reverse(
            'comments-edit',
            args=[
                self.post.id,
                self.comment.id])

    def test_get_comment_successfully(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertEqual(response.context['form'].instance, self.comment)

    def test_edit_comment_successfully(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('comments-edit', args=[self.post.id, self.comment.id])
        data = {
            'content': 'Updated comment content',
            'name': 'tag1, tag2'
        }
        response = self.client.post(url, data)
        comment = Comment.objects.get(id=self.comment.id)
        tags = comment.tags.all()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'all-comments-for-post', args=[self.post.id]))
        self.assertEqual(comment.content, 'Updated comment content')
        self.assertEqual(tags.count(), 2)
        self.assertEqual(tags[0].tag.name, 'tag1')
        self.assertEqual(tags[1].tag.name, 'tag2')


class TestDeleteCommentView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, caption='test caption')
        self.comment = Comment.objects.create(
            user=self.user, post=self.post, content='Test Comment')
        self.url = reverse(
            'comments-delete',
            args=[self.post.id, self.comment.id])

    def test_get_comment_confirmation_page_successfully(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_successfully(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('all-comments-for-post', args=[self.post.id]))
        self.assertFalse(Comment.objects.filter(pk=self.comment.id).exists())

    def test_delete_comment_unauthorized_user(self):
        unauthorized_user = User.objects.create_user(
            username='unauthorizeduser', password='testpass')
        self.client.login(username='unauthorizeduser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(pk=self.comment.id).exists())
