import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from webapp.forms import RegisterForm, LoginForm, PostForm, CommentForm, PostImageForm, BioForm, PostTagForm
from webapp.models import Post, Comment, Tag, UserProfile, PostTag, CommentTag, PostImage, Subscription


class TestSignUpView(TestCase):
    def setUp(self):
        """
        Set up the test environment before running each test case.
        :param self: The instance of the test case.
        """
        self.client = Client()
        self.login_url = reverse('register')
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com',
                                             password='testpassword123')

    def test_get(self):
        """
        A test function to check the behavior of the 'get' method.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/register.html')
        self.assertTrue(isinstance(response.context['form'], RegisterForm))

    def test_post_valid(self):
        """
        A function to test the validity of a post request.
        """
        data = {'username': 'testuser', 'email': 'testuser@example.com', 'password1': 'testpassword123',
            'password2': 'testpassword123', }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)


class TestSignInView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables required for testing.
        This function initializes the client object, sets the login URL, and creates a test user.
        """
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_get(self):
        """
        Test the 'get' method of the class.
        This method sends a GET request to the login URL and asserts that the response
        status code is 200. It also asserts that the 'login.html' template is used and
        that the context contains a 'form' object of type 'LoginForm'.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/login.html')
        self.assertTrue(isinstance(response.context['form'], LoginForm))

    def test_post_valid(self):
        """
        Test the validity of a POST request.
        This function sends a POST request to the login URL with a valid username and password.
         It then asserts that the response status code is 302 (redirect). Finally, it asserts that the response redirects to the 'posts' URL.
        """
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('posts'))


class TestSingOutView(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a client, setting the logout URL, and creating a test user.
        """
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_get(self):
        """
        A test case for the `get` method of the class.
        This test case ensures that when the user is logged in and the `get` method of
        the client is called with the `logout_url`, the response status code is `302`,
        indicating a redirection.
        Additionally, it checks if the response redirects to the `login` page and
        that the `_auth_user_id` key is not present in the client session.
        """
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)


class TestSubscribeView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for testing.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, full_name='Test User')
        self.user_to_subscribe = User.objects.create_user(username='testuser2', password='testpass2')
        self.url = reverse('subscribe', args=[self.user_to_subscribe.id])

    def test_subscribe_post_successfully(self):
        """
        Test the successful subscription when making a POST request.
        This function tests the successful subscription process by performing the following steps:
        - Login as the test user.
        - Make a POST request to the specified URL.
        - Assert that the response status code is 200.
        - Assert that the response content type is 'application/json'.
        - Load the response content as JSON.
        - Assert that the 'is_subscribed' key is present in the JSON data.
        - Assert that the value of 'is_subscribed' is True.
        - Assert that the user's profile has a subscription to the user being subscribed to.
        - Assert that a subscription object exists for the user and the user being subscribed to.
        """
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
        """
        Set up the test environment by creating a client instance,
        a user instance with the username 'testuser' and password 'testpass',
        and a user profile instance with the full name 'Test User'.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, full_name='Test User')

    def test_feed_view(self):
        """
        Test the view for the feed page.
        This function tests the behavior of the feed view by performing the following steps:
        - Logs in the test user with the username 'testuser' and password 'testpass'.
        - Sends a GET request to the 'feed' URL using the Django test client.
        - Asserts that the response status code is 200.
        - Asserts that the 'feed.html' template is used to render the response.
        - Asserts that the 'posts' queryset in the response context is empty.
        - Creates two Post objects with the test user as the author and different captions.
        - Sends another GET request to the 'feed' URL.
        - Asserts that the response status code is 200.
        """
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
        """
        Set up the necessary objects and data for the test.
        This function initializes the `self.client` attribute with a new instance
        of the `Client` class. It also creates a new user with the username
        'testuser' and password '12345' using the `User.objects.create_user`
        method. The function then logs in the user using the `self.client.login`
        method with the username and password. Finally, it creates a new post
        with the caption 'Test Post' and author set to the created user using
        the `Post.objects.create` method.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.post = Post.objects.create(caption='Test Post', author=self.user)

    def test_home_view(self):
        """
        Test the home view.
        This function tests the home view by sending a GET request to the 'posts' URL and
        checking that the response status code is 200. It also checks that the 'home.html'
        template is used and that the response contains the text 'Test Post'.
        """
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/home.html')
        self.assertContains(response, 'Test Post')

    def test_home_view_with_no_login(self):
        """
        Test the home view when the user is not logged in.
        This function logs the user out, sends a GET request to the 'posts' URL, and
        asserts that the response status code is 302 (redirect). It also asserts that
        the response redirects to the login page with the correct next parameter.
        """
        self.client.logout()
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=%2F')


class TestLikePostView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and data for the test case.
        This function creates a user with the username 'testuser' and the password 'password123',
        and creates a post with the caption 'Test Post' and the author set to the created user.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = Post.objects.create(caption='Test Post', author=self.user)

    def test_like_post(self):
        """
        Test for liking a post.
        This function tests the functionality of liking a post. It performs the following steps:
        - Creates a new client object.
        - Logs in using the username 'testuser' and password 'password123'.
        - Sends a POST request to the 'like-post' endpoint, passing the post ID as an argument.
        - Asserts that the response status code is 200.
        - Asserts that the response content-type is 'application/json'.
        - Parses the response content as JSON.
        - Asserts that the parsed JSON contains the key 'is_liked'.
        - Asserts that the value of 'is_liked' in the parsed JSON is True.
        - Asserts that the parsed JSON contains the key 'likes_count'.
        - Asserts that the value of 'likes_count' in the parsed JSON is 1.
        - Asserts that the number of likes on the post is 1.
        """
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
        """
        Set up the test environment by creating a user, a post, and a comment.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = Post.objects.create(caption='Test Post', author=self.user)
        self.comment = Comment.objects.create(post=self.post, user=self.user, content='This is a test comment.')

    def test_like_comment(self):
        """
        Test the functionality of liking a comment.
        This function performs the following steps:
        - Creates a new instance of the Client class.
        - Logs in the client using the provided username and password.
        - Sends a POST request to the 'like-comment' endpoint with the post ID and comment ID as arguments.
        - Asserts that the response status code is 200.
        - Asserts that the response content type is 'application/json'.
        - Parses the response content as JSON.
        - Asserts that the 'is_liked' key is present in the parsed JSON data.
        - Asserts that the value of the 'is_liked' key is True.
        - Asserts that the 'likes_count' key is present in the parsed JSON data.
        - Asserts that the value of the 'likes_count' key is 1.
        - Asserts that the number of likes on the comment is 1.
        """
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
        """
        Set up the necessary objects and variables for testing.
        This function initializes the client object and creates a test user with
        a username of 'testuser' and a password of 'testpass'.
        It also creates a user profile for the test user with a bio of 'Test bio'.
        Finally, it sets the URL for the 'user-information' endpoint.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, bio='Test bio')
        self.url = reverse('user-information')

    def test_get_with_authenticated_user(self):
        """
        Test the `get` method when the user is authenticated.
        This test case ensures that the `get` method of the API returns the expected response
        when the user is authenticated. It performs the following steps:
        1. Logs in the user with the provided `username` and `password`.
        2. Sends a `GET` request to the specified URL.
        3. Asserts that the response status code is `200`.
        4. Asserts that the template used for rendering the response is `'webapp/user_info.html'`.
        5. Asserts that the response body contains the string `'Test bio'`.
        This test case is intended to verify the behavior of the `get` method when the user is
        authenticated.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/user_info.html')
        self.assertContains(response, 'Test bio')

    def test_get_with_unauthenticated_user(self):
        """
        Test case for the `get` method when the user is unauthenticated.
        This test verifies that when an unauthenticated user sends a GET request to the specified URL,
        the user is redirected to the login page with the correct `next` parameter.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_get_with_no_bio(self):
        """
        Test the behavior of the 'get' method when the user profile has no bio.
        This test verifies that when a user profile does not have a bio, the 'get'
        method of the view redirects to the 'user-bio-create' URL.
        """
        self.client.login(username='testuser', password='testpass')
        self.user_profile.delete()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user-bio-create'))


class TestUserBioCreateView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for the test case.
        This function initializes the following objects and variables:
        - self.client: an instance of the Client class.
        - self.user: an instance of the User model created using the
          create_user() method of the User.objects object.
        - self.url: a string representing the URL of the 'user-bio-create'
          route.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.url = reverse('user-bio-create')

    def test_get_with_authenticated_user(self):
        """
        Test the get method when the user is authenticated.
        This method tests the behavior of the get method when the user is authenticated.
        It performs the following steps:
        1. Logs in with the test user credentials.
        2. Sends a GET request to the specified URL.
        3. Asserts that the response status code is 200.
        4. Asserts that the 'webapp/bio_user.html' template is used.
        5. Asserts that the 'form' key in the response context is an instance of BioForm.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')
        self.assertIsInstance(response.context['form'], BioForm)

    def test_get_with_unauthenticated_user(self):
        """
        Test the behavior of the `get` method when called with an unauthenticated user.
        This function sends a GET request to the specified URL using the client object.
        It then asserts that the response is a redirect to the login page with the appropriate
        next parameter set.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_post_with_valid_data(self):
        """
        Test the functionality of posting with valid data.
        This function is used to test the behavior of the `post` method in the Django `Client`
        class when valid data is provided. It performs the following steps:
        1. Logs in the client using the username and password 'testuser' and 'testpass'.
        2. Constructs a dictionary `data` containing the values for the fields 'full_name' and 'bio'.
        3. Sends a POST request to the URL specified by `self.url` with the data from step 2.
        4. Asserts that the response is a redirect to the 'user-information' page.
        5. Asserts that a `UserProfile` object is created for the `self.user` user.
        6. Asserts that the `bio` attribute of the `UserProfile` object matches the value 'New test bio'.
        """
        self.client.login(username='testuser', password='testpass')
        data = {'full_name': 'testuser', 'bio': 'New test bio'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('user-information'))
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)
        self.assertEqual(UserProfile.objects.get(user=self.user).bio, 'New test bio')

    def test_post_with_invalid_data(self):
        """
        Test the behavior of the `post` method when invalid data is provided.
        This function tests if the `post` method of the client behaves correctly
        when invalid data is provided. It performs the following steps:
        1. Logs in the client using the username and password.
        2. Creates a data dictionary with an empty `bio` field.
        3. Sends a POST request to the specified URL with the data.
        4. Asserts that the response status code is 200.
        5. Asserts that the response template used is 'webapp/bio_user.html'.
        6. Asserts that the response context contains a form instance of the `BioForm` class.
        7. Asserts that the response contains the expected error message.
        """
        self.client.login(username='testuser', password='testpass')
        data = {'bio': ''}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')
        self.assertIsInstance(response.context['form'], BioForm)
        self.assertContains(response, 'Please correct the following errors:')


class TestUserBioEditView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and data for testing the user edit endpoint.
        This function initializes the following objects and data:
            - self.client: An instance of the Django test client.
            - self.user: A user object created using the User.objects.create_user() method.
            - self.userprofile: A user profile object created using the UserProfile.objects.create() method.
            - self.url: The URL for the user edit endpoint, generated using the reverse() method.
            - self.data: A dictionary containing test data for the user edit request.
        This function is executed before each test case in the test suite.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.userprofile = UserProfile.objects.create(user=self.user, bio='This is a test bio')
        self.url = reverse('user-edit', args=[self.userprofile.id])
        self.data = {'full_name': 'testuser', 'bio': 'This is a test bio edit'}

    def test_get(self):
        """
        Test the `get` method of the API.
        This function logs in the test user, sends a GET request
        to the specified URL, and asserts that the response status code is 200.
        It also asserts that the 'webapp/bio_user.html' template is used.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/bio_user.html')

    def test_post(self):
        """
        This function is used to test the POST functionality of a specific API endpoint.

        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-information'))
        self.userprofile.refresh_from_db()
        self.assertEqual(self.userprofile.bio, 'This is a test bio edit')


class TestCreatePostView(TestCase):
    def setUp(self):
        """
        Set up the necessary resources and environment for testing.
        This function initializes the client, creates a test user
        with a username of 'testuser' and a password of 'testpass',
        logs in the test user using the provided credentials,
        and sets the URL for creating a new post.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('post-create')

    def test_get(self):
        """
        Test the GET method of the API.
        This function sends a GET request to the specified URL and performs several assertions
        to ensure the correct behavior of the API. It checks that the response status code is
        200, that the 'webapp/post_form.html' template is used, and that the 'form',
        'post_image_form', and 'tag_form' variables in the response context are instances of
        the expected classes.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/post_form.html')
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsInstance(response.context['post_image_form'], PostImageForm)
        self.assertIsInstance(response.context['tag_form'], PostTagForm)

    def test_post_valid_form(self):
        """
        Test the functionality of posting a valid form.
        This function tests the functionality of posting a valid form by simulating a form submission with
        the following data:
        - 'caption': 'Test post'
        - 'images-0-image': 'test_image.jpg' (a SimpleUploadedFile object with content type 'image/jpeg')
        - 'name': 'test1, test2'
        The function then makes a POST request to the specified URL using the Django client and checks the
        response status code, as well as the number of objects in the Post, PostImage, Tag, and PostTag models.
        It asserts that the response status code is 302 (indicating a successful redirect), the number of
        Post objects is 1, the number of PostImage objects is 1, the number of Tag objects is 2, and the number
        of PostTag objects is 2.
        This function is part of the test suite for the specified class and should be run to ensure the correct
        functionality of the post_valid_form method.
        """
        data = {'caption': 'Test post',
                'images-0-image': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
                'name': 'test1, test2', }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(PostImage.objects.count(), 1)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(PostTag.objects.count(), 2)


class TestEditPostView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for the test case.
        """
        self.client = Client()

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='Test caption')
        self.url = reverse('post-edit', args=[self.post.pk])

    def test_get_edit_post_view(self):
        """
        Test the functionality of the 'get_edit_post_view' method.
        The 'get_edit_post_view' method is responsible for handling the HTTP GET request
        to the edit post view. This method performs the following tasks:
        - Logs in the user with the provided username and password.
        - Sends a GET request to the specified URL.
        - Asserts that the response status code is 200.
        - Asserts that the 'post_form.html' template is used.
        - Asserts that the 'form' attribute in the response context is an instance of PostForm.
        - Asserts that the 'post_image_form' attribute in the response context is an instance of PostImageForm.
        - Asserts that the 'tag_form' attribute in the response context is an instance of PostTagForm.
        - Asserts that the 'post_tags' queryset in the response context is equal to the tags of the post.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/post_form.html')
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIsInstance(response.context['post_image_form'], PostImageForm)
        self.assertIsInstance(response.context['tag_form'], PostTagForm)
        self.assertQuerysetEqual(response.context['post_tags'], self.post.tags.all(), transform=lambda x: x)

    def test_post_edit_post_view(self):
        """
        Test the functionality of the post_edit_post_view.
        This function tests the post_edit_post_view to ensure that it is functioning as expected.
        It performs the following steps:
        1. Logs in the test user with the provided username and password.
        2. Creates a SimpleUploadedFile object to simulate an image file.
        3. Constructs a dictionary containing the data to be sent in the post request.
        4. Sends a post request to the specified URL with the constructed data.
        5. Performs assertions to verify the status code, updated caption, and presence of an image in the post.
        """
        self.client.login(username='testuser', password='testpass')
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        data = {'caption': 'New test caption', 'avatar': image_file, 'name': 'tag1, tag2'}
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.caption, 'New test caption')
        self.assertIsNotNone(self.post.images.first())


class TestDeletePostView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and data for the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='Test post')

    def test_authenticated_user_can_access_view(self):
        """
        Test if an authenticated user can access a specific view.
        This function logs in a user with the given username and password,
        then sends a GET request to the 'post-delete' view with the argument 1.
        It checks if the response status code is equal to 200.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('post-delete', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_view(self):
        """
        Test that an unauthenticated user cannot access the view.
        This function sends a GET request to the specified URL and checks if the response
        status code is equal to 302. It also asserts that the user is redirected to the
        login page with the appropriate next URL.
        """
        response = self.client.get(reverse('post-delete', args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/posts/delete/1/')

    def test_post_successfully_deleted_from_database(self):
        """
        Test if a post is successfully deleted from the database.
        This method performs the following steps:
        1. Logs in the test user with the username 'testuser' and password 'testpass'.
        2. Sends a POST request to the 'post-delete' endpoint with the post ID as an argument.
        3. Asserts that the post does not exist in the database anymore.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('post-delete', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(pk=self.post.id).exists())


class TestAllCommentsForPostView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for testing.
        This function initializes the client, creates a test user, creates a test post,
        creates a test comment, and sets the URL for retrieving all comments for the post.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='Test post', )
        self.comment = Comment.objects.create(user=self.user, post=self.post, content='Test comment')
        self.url = reverse('all-comments-for-post', args=[self.post.pk])

    def test_get_comments_for_valid_post(self):
        """
        Test case to get comments for a valid post.
        This test case checks if the user is able to retrieve comments for a valid post.
        It logs in the user with the username 'testuser' and password 'testpass'.
        Then, it sends a GET request to the specified URL and verifies that the response
        status code is 200. Finally, it asserts that the template used for rendering
        the response is 'webapp/comments_post.html'.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'webapp/comments_post.html')

    def test_multiple_comments_for_post(self):
        """
        Test if multiple comments are correctly displayed for a post.
        This function logs in a test user, creates two test comments for a post,
        and then sends a GET request to the specified URL.
        It asserts that the response status code is 200 and that both comments
        are included in the response context.
        """
        self.client.login(username='testuser', password='testpass')
        comment1 = Comment.objects.create(user=self.user, post=self.post, content='Test comment 1')
        comment2 = Comment.objects.create(user=self.user, post=self.post, content='Test comment 2')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(comment1, response.context['comments'])
        self.assertIn(comment2, response.context['comments'])

    def test_invalid_post_id(self):
        """
        Test the case where an invalid post ID is provided.
        This function sends a GET request to the '/comments/999/' endpoint of the client.
        It then checks if the response status code is equal to 404, indicating that the
        requested resource was not found.
        """
        response = self.client.get('/comments/999/')
        self.assertEqual(response.status_code, 404)

    def test_rendering_template(self):
        """
        Test the rendering of a template.
        This function logs in a test user and makes a GET request to a specific URL.
        It then asserts that the template used in the response is 'webapp/comments_post.html'.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'webapp/comments_post.html')

    def test_context_contains_correct_data(self):
        """
        Test if the context contains the correct data after executing the function.
        This function logs in a test user, sends a GET request to a specific URL,
        and then asserts that the response
        contains the correct data in its context.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.context['post'], self.post)
        self.assertIn(self.comment, response.context['comments'])


class TestCommentsForPostCreateView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for testing.
        This function initializes the `client` attribute with an instance of the `Client` class.
        It also creates a test user by calling the `create_user` method of the `User` object and assigns
        it to the `user` attribute.
        Additionally, it creates a test post by calling the `create` method of the `Post` object
        and assigns it to the `post` attribute.
        Finally, it sets the `url` attribute with the URL for creating comments for the test post.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='test caption', )
        self.url = reverse('comments-create', args=[self.post.pk])

    def test_comment_creation_success(self):
        """
        Test that a comment is created successfully with valid comment and
        tag forms.
        """
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': 'test comment', 'name': 'tag1, tag2'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 2)
        self.assertEqual(len(CommentTag.objects.all()), 2)

    def test_comment_creation_success_empty_tag(self):
        """
        Test that a comment is created successfully with valid comment form and empty tag form.
        """
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': 'test comment', 'name': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 0)
        self.assertEqual(len(CommentTag.objects.all()), 0)

    def test_comment_creation_failure_invalid_form(self):
        """
        Test that an error message is displayed when the comment form is invalid.
        """
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the following errors:')
        self.assertEqual(len(Comment.objects.all()), 0)
        self.assertEqual(len(Tag.objects.all()), 0)
        self.assertEqual(len(CommentTag.objects.all()), 0)

    def test_comment_creation_failure_duplicate_tags(self):
        """
        Test that only unique tags are created when the tag form contains duplicate tags.
        """
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': 'test comment', 'name': 'tag1, tag1'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 1)
        self.assertEqual(len(CommentTag.objects.all()), 2)

    def test_comment_creation_success_invalid_tag(self):
        """
        Test that a comment is created successfully with valid comment form and invalid tag form.
        """
        self.client.force_login(self.post.author)
        response = self.client.post(self.url, {'content': 'test comment', 'name': 'tag1, , tag2'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Tag.objects.all()), 3)
        self.assertEqual(len(CommentTag.objects.all()), 3)


class TestEditCommentView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and data for the test case.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='test caption', )
        self.comment = Comment.objects.create(user=self.user, post=self.post, content='Test Comment')
        self.data = {'user': self.user, 'post': self.post, 'caption': 'Test post',
                     'images-0-image': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
                     'content': 'Updated Comment', 'name': 'test1, test2', }
        self.url = reverse('comments-edit', args=[self.post.id, self.comment.id])

    def test_get_comment_successfully(self):
        """
        Test the successful retrieval of a comment by the API.
        This test function logs in a test user, sends a GET request to the specified URL
        with the given data, and verifies that the response status code is 200.
        It also checks that the context variable 'form' is an instance of CommentForm
        and that the 'instance' attribute of the 'form' variable is equal to the self.comment object.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertEqual(response.context['form'].instance, self.comment)

    def test_edit_comment_successfully(self):
        """
        Test the successful editing of a comment.
        This test function performs the following actions:
        1. Logs in the test user.
        2. Retrieves the URL for editing a comment for a specific post and comment.
        3. Sends a POST request to the edit comment URL with updated comment content and tags.
        4. Retrieves the updated comment object from the database.
        5. Retrieves all tags associated with the updated comment.
        6. Asserts that the response status code is 302 (redirect).
        7. Asserts that the response redirects to the correct URL.
        8. Asserts that the comment's content is updated correctly.
        9. Asserts that the number of tags associated with the comment is 2.
        10. Asserts that the first tag's name is 'tag1'.
        11. Asserts that the second tag's name is 'tag2'.
        """
        self.client.login(username='testuser', password='testpass')
        url = reverse('comments-edit', args=[self.post.id, self.comment.id])
        data = {'content': 'Updated comment content', 'name': 'tag1, tag2'}
        response = self.client.post(url, data)
        comment = Comment.objects.get(id=self.comment.id)
        tags = comment.tags.all()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('all-comments-for-post', args=[self.post.id]))
        self.assertEqual(comment.content, 'Updated comment content')
        self.assertEqual(tags.count(), 2)
        self.assertEqual(tags[0].tag.name, 'tag1')
        self.assertEqual(tags[1].tag.name, 'tag2')


class TestDeleteCommentView(TestCase):
    def setUp(self):
        """
        Set up the necessary objects and variables for the test case.
        This function initializes the following objects and variables:
        - `self.client`: An instance of the `Client` class.
        - `self.user`: An instance of the `User` model created with the username 'testuser' and password 'testpass'.
        - `self.post`: An instance of the `Post` model created with the author set to `self.user` and the caption set to 'test caption'.
        - `self.comment`: An instance of the `Comment` model created with the user set to `self.user`, the post set to `self.post`, and the content set to 'Test Comment'.
        - `self.url`: A URL generated using the `reverse` function with the arguments `[self.post.id, self.comment.id]`.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(author=self.user, caption='test caption')
        self.comment = Comment.objects.create(user=self.user, post=self.post, content='Test Comment')
        self.url = reverse('comments-delete', args=[self.post.id, self.comment.id])

    def test_get_comment_confirmation_page_successfully(self):
        """
        Test the functionality of getting the comment confirmation page successfully.
        This function logs in a test user, sends a GET request to the specified URL,
        and asserts that the response status code is 200.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_comment_successfully(self):
        """
        Test that the comment is deleted successfully.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('all-comments-for-post', args=[self.post.id]))
        self.assertFalse(Comment.objects.filter(pk=self.comment.id).exists())

    def test_delete_comment_unauthorized_user(self):
        """
        Test the behavior of deleting a comment when the user is unauthorized.
        This function creates an unauthorized user and logs them in.
        Then it sends a POST request to the specified URL.
        Finally, it asserts that the response status code is 302 and checks
        if the comment still exists in the database.
        """
        unauthorized_user = User.objects.create_user(username='unauthorizeduser', password='testpass')
        self.client.login(username='unauthorizeduser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(pk=self.comment.id).exists())
