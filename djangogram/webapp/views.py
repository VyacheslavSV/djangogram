from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .forms import PostForm, PostImageForm, BioForm, CommentForm, PostTagForm, CommentTagForm, LoginForm, RegisterForm, \
    User
from .models import Post, UserProfile, Tag, Comment, PostTag, PostLike, CommentTag, CommentLike, Subscription


class SignUpView(View):
    def get(self, request):
        """
        Renders the 'register.html' template with an instance of the RegisterForm.
        :param request: The HTTP request object.
        :return: The rendered 'register.html' template with the form instance.
        """
        form = RegisterForm()
        return render(request, 'webapp/register.html', {'form': form})

    def post(self, request):
        """
        Handles the POST request for the API endpoint.
        Parameters:
            request (HttpRequest): The HTTP request object containing the POST data.
        Returns:
            HttpResponse: The HTTP response object.
        """
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have singed up successfully.')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user-bio-create')
        return render(request, 'webapp/register.html', {'form': form})


class SignInView(View):

    def get(self, request):
        """
        Retrieves the requested resource.
        Args:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: The HTTP response object.
        """
        if request.user.is_authenticated:
            return redirect('user-information')
        form = LoginForm()
        return render(request, 'webapp/login.html', {'form': form})

    def post(self, request):
        """
        Handle the HTTP POST request to authenticate the user.
        Parameters:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: The HTTP response object.
        Description:
            This function handles the HTTP POST request to authenticate the user.
            It takes in a request object and performs the following steps:
            1. Validate the login form data.
            2. If the form data is valid, authenticate the user.
            3. If the user is authenticated, log them in and display a welcome message.
            4. Redirect the user to the 'posts' page.
            5. If the form data is invalid, display an error message.
            6. Render the login page with the login form.
        Note:
            - This function assumes that a 'LoginForm' class has been defined.
            - The 'LoginForm' class should have 'username' and 'password' fields.
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Hi {username.title()}, welcome back!')
                return redirect('posts')
        messages.error(request, f'Invalid username or password')
        return render(request, 'webapp/login.html', {'form': form})


class SingOutView(View):
    def get(self, request):
        """
        Perform the logout process for a user.
        Parameters:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponseRedirect: A redirect to the login page.
        """
        logout(request)
        messages.success(request, f'You have been logged out.')
        return redirect('login')


class SubscribeView(View):
    @method_decorator(login_required)
    def post(self, request, user_id):
        """
        Handles the POST request for subscribing/unsubscribing to a user.
        Args:
            request (HttpRequest): The HTTP request object.
            user_id (int): The ID of the user to subscribe/unsubscribe.
        Returns:
            JsonResponse: A JSON response indicating whether the user is subscribed or unsubscribed.
                The response has the following format:
                {
                    'is_subscribed': bool,  # Indicates whether the user is subscribed or unsubscribed.
                }
        """
        user = get_object_or_404(User, id=user_id)
        if Subscription.objects.filter(user=request.user, subscribed_to=user):
            request.user.profile.subscriptions.remove(user)
            Subscription.objects.filter(user=request.user, subscribed_to=user).delete()
            is_subscribed = False
        else:
            request.user.profile.subscriptions.add(user)
            Subscription.objects.create(user=request.user, subscribed_to=user)
            is_subscribed = True
        response = {'is_subscribed': is_subscribed, }
        return JsonResponse(response)


class FeedView(View):
    def get(self, request):
        """
        Get the feed posts for the given user and render them in the feed.html template.
        Parameters:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: The rendered feed.html template with the feed posts.
        """
        posts = Post.objects.get_feed_posts(request.user)
        context = {'posts': posts}
        return render(request, 'webapp/feed.html', context)


class HomeView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        This function is the GET method of a class-based view.
        It is decorated with the login_required decorator,
        which ensures that only authenticated users can access this view.
        Parameters:
            - request: The HTTP request object.
        Returns:
            - A rendered HTML template ('webapp/home.html') with the 'posts' context variable.
        """
        posts = Post.objects.all().prefetch_related('images', 'tags')
        context = {'posts': posts}
        return render(request, 'webapp/home.html', context)


class LikePostView(View):
    @method_decorator(login_required)
    def post(self, request, post_id):
        """
        Handles the HTTP POST request to like or unlike a post.
        Parameters:
            request (HttpRequest): The HTTP request object.
            post_id (int): The ID of the post to like or unlike.
        Returns:
            JsonResponse: A JSON response containing the updated like status
            and the total number of likes for the post.
        """
        post = get_object_or_404(Post, id=post_id)
        if request.user.is_authenticated:
            try:
                like = post.likes.get(user=request.user)
                like.delete()
                is_liked = False
            except PostLike.DoesNotExist:
                like = PostLike.objects.create(post=post, user=request.user)
                is_liked = True
            response = {'is_liked': is_liked, 'likes_count': post.likes.count(), }
            return JsonResponse(response)


class LikeCommentView(View):
    @method_decorator(login_required)
    def post(self, request, post_id, comment_id):
        """
        Handles the POST request to like or unlike a comment.
        Parameters:
            - request (Request): The HTTP request object.
            - post_id (int): The ID of the post.
            - comment_id (int): The ID of the comment.
        Returns:
            - JsonResponse: A JSON response containing the result of the like operation.
        """
        comment = get_object_or_404(Comment, id=comment_id)
        post = get_object_or_404(Post, id=post_id)
        if request.user.is_authenticated:
            liked_comments = CommentLike.objects.filter(comment=comment, user=request.user)
            if liked_comments.exists():
                liked_comments.delete()
                is_liked = False
            else:
                CommentLike.objects.create(comment=comment, user=request.user)
                is_liked = True
            response = {'is_liked': is_liked, 'likes_count': liked_comments.count(), }
            return JsonResponse(response)


class UserBioView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Decorated function that handles the HTTP GET request for the given view.
        Args:
            request (HttpRequest): The HTTP GET request object.
        Returns:
            HttpResponse: The HTTP response object.
        """
        bio = UserProfile.objects.filter(user=request.user)
        context = {'bio': bio}
        if bio:
            return render(request, 'webapp/user_info.html', context)
        return redirect('user-bio-create')


class UserBioCreateView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        Decorates the `get` method to require login before execution.
        Parameters:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: The rendered response containing the 'webapp/bio_user.html' template.
        """
        context = {'form': BioForm()}
        return render(request, 'webapp/bio_user.html', context)

    @method_decorator(login_required)
    def post(self, request):
        """
        Handles the POST request to create a new bio.
        Parameters:
            - request (HttpRequest): The HTTP request object.
        Returns:
            - HttpResponseRedirect: If the form is valid, redirects to the 'user-information' page.
        """
        form = BioForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.user = request.user
            user.save()
            messages.success(request, 'The bio has been created successfully.')
            return redirect('user-information')
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/bio_user.html', {'form': form})


class UserBioEditView(View):
    @method_decorator(login_required)
    def get(self, request, id):
        """
        This function is a view function that handles GET requests for a specific user's bio page.
        Parameters:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the user's profile.
        Returns:
            HttpResponse: The rendered HTML response containing the user's bio page.
        """
        queryset = UserProfile.objects.filter(user=request.user)

        post = get_object_or_404(queryset, pk=id)
        context = {'form': BioForm(instance=post), 'id': id}
        return render(request, 'webapp/bio_user.html', context)

    @method_decorator(login_required)
    def post(self, request, id):
        """
        Handles the HTTP POST request for updating the bio of a user profile.
        Args:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the user profile to update.
        Returns:
            HttpResponse: The HTTP response object.
        Raises:
            Http404: If the user profile with the given ID does not exist.
        Notes:
            - This function requires the user to be logged in.
            - The bio is updated based on the form data submitted in the request.
            - If the form data is valid, the bio is updated and a success message is displayed.
            - If the form data is invalid, an error message is displayed with the form errors.
        """
        queryset = UserProfile.objects.filter(user=request.user)
        post = get_object_or_404(queryset, pk=id)
        form = BioForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'The bio has has been updated successfully.')
            return redirect('user-information')
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/bio_user.html', {'form': form})


class CreatePostView(View):
    @method_decorator(login_required)
    def get(self, request):
        """
        A decorator that requires the user to be logged in to access the function.
        Args:
            request: The request object that contains the HTTP request information.
        Returns:
            The rendered HTML template for the 'webapp/post_form.html' page.
        """
        context = {'form': PostForm(), 'post_image_form': PostImageForm(), 'tag_form': PostTagForm()}
        return render(request, 'webapp/post_form.html', context)

    @method_decorator(login_required)
    def post(self, request):
        """
        Handles the HTTP POST request for creating a new post.
        :param request: The HTTP request object.
        :type request: django.http.HttpRequest
        :return: The HTTP response object.
        :rtype: django.http.HttpResponse
        """
        form = PostForm(request.POST)
        post_image_form = PostImageForm(request.POST, request.FILES)
        tag_form = PostTagForm(request.POST)
        if form.is_valid() and post_image_form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            post_image = post_image_form.save(commit=False)
            post_image.post = post
            post_image.save()

            if tag_form.is_valid():
                tag_name = tag_form.cleaned_data['name'].split(',')
                for name in tag_name:
                    name = name.strip()
                    tag, created = Tag.objects.get_or_create(name=name)
                    post_tags = PostTag.objects.create(post=post, tag=tag)
            messages.success(request, 'The post has been created successfully.')
            return redirect('posts')
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/post_form.html',
                      {'form': form, 'post_image_form': post_image_form, 'tag_form': tag_form})


class EditPostView(View):
    @method_decorator(login_required)
    def get(self, request, post_id):
        """
        Retrieves a specific post for editing.
        Args:
            request (HttpRequest): The request object.
            post_id (int): The ID of the post to retrieve.
        Returns:
            HttpResponse: The rendered post form template with the retrieved post data.
        """
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {'form': PostForm(instance=post), 'post_image_form': PostImageForm(instance=post.images.first()),
            'tag_form': PostTagForm(), 'post_tags': post.tags.all()}
        return render(request, 'webapp/post_form.html', context)

    @method_decorator(login_required)
    def post(self, request, post_id):
        """
        Handles the HTTP POST request for updating a post.
        This method is decorated with the `login_required` decorator,
        which ensures that only authenticated users can access this endpoint.
        Parameters:
        - request (HttpRequest): The HTTP request object.
        - post_id (int): The ID of the post to be updated.
        Returns:
        - HttpResponseRedirect: A redirect response to the 'posts' URL if the post is updated successfully.
        Raises:
        - Http404: If the specified post does not exist.
        Notes:
        - This method first filters the `Post` objects by the current user, using the `author` field of the `Post` model.
        - It then retrieves the post to be updated using the `get_object_or_404` function,
        which raises a `Http404` exception if the post does not exist.
        - The `PostForm` is initialized with the request data and the post instance.
        - The `PostImageForm` is also initialized with the request data and the first image of the post, if it exists.
        - The `PostTagForm` is initialized with the request data.
        - If the form is valid, the post is saved.
        - If the post image form is valid, a new `PostImage` object is created and associated with the post.
        - If the tag form is valid, new `PostTag` objects are created for each tag name provided.
        - A success message is added to the request object.
        - Finally, the user is redirected to the 'posts' URL.
        """
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        form = PostForm(request.POST, instance=post)
        post_image_form = PostImageForm(request.POST, request.FILES, instance=post.images.first())
        tag_form = PostTagForm(request.POST)

        if form.is_valid():
            form.save()

            if post_image_form.is_valid():
                post_image = post_image_form.save(commit=False)
                post_image.post = post
                post_image_form.save()

            if tag_form.is_valid():
                tag_names = tag_form.cleaned_data['name'].split(',')
                for name in tag_names:
                    name = name.strip()
                    tag, created = Tag.objects.get_or_create(name=name)
                    post_tags = PostTag.objects.create(post=post, tag=tag)
            messages.success(request, 'The post has been updated successfully.')
            return redirect('posts')
        context = {'form': form, 'post_image_form': post_image_form, 'tag_form': tag_form, 'post_tags': post.tags.all()}
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/post_form.html', context)


class DeletePostView(View):
    @method_decorator(login_required)
    def get(self, request, post_id):
        """
        Decorated function that handles the GET request for a specific post.
        Parameters:
            request (HttpRequest): The request object.
            post_id (int): The ID of the post.
        Returns:
            HttpResponse: The rendered HTML page for post_confirm_delete.html.
        """
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {'post': post}
        return render(request, 'webapp/post_confirm_delete.html', context)

    @method_decorator(login_required)
    def post(self, request, post_id):
        """
        Deletes a post from the database and redirects the user to the 'posts' page.
        Parameters:
            request (HttpRequest): The HTTP request object.
            post_id (int): The ID of the post to be deleted.
        Returns:
            HttpResponseRedirect: A redirect response to the 'posts' page.
        """
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {'post': post}
        post.delete()
        messages.success(request, 'The post has been deleted successfully.')
        return redirect('posts')


class AllCommentsForPostView(View):
    @method_decorator(login_required)
    def get(self, request, id):
        """
        Renders the comments of a post.
        Parameters:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the post.
        Returns:
            HttpResponse: The rendered HTML page containing the comments of the post.
        """
        post = get_object_or_404(Post, id=id)
        comments = Comment.objects.filter(post=post)
        context = {'post': post, 'comments': comments}
        return render(request, 'webapp/comments_post.html', context)


class CommentsForPostCreateView(View):
    @method_decorator(login_required)
    def get(self, request, id):
        """
        Renders the comment form page.
        Parameters:
            request (HttpRequest): The request object.
            id (int): The id of the comment.
        Returns:
            HttpResponse: The rendered comment form page.
        """
        context = {'form': CommentForm(), 'tag_form': CommentTagForm()}
        return render(request, 'webapp/comment_form.html', context)

    @method_decorator(login_required)
    def post(self, request, id):
        """
        Handles the HTTP POST request for creating a new comment.
        Args:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the post to add the comment to.
        Returns:
            HttpResponseRedirect: The redirect response to the page showing all comments for the post.
        Raises:
            Http404: If the specified post does not exist.
        Notes:
            - This function is decorated with the `login_required` decorator to ensure that the user is authenticated.
            - The function creates a new instance of the `CommentForm` and `CommentTagForm` classes using the data from the POST request.
            - If the form is valid, the function saves the comment object to the database and associates it with the specified post.
            - If the tag form is valid, the function creates comment tag objects for each tag name provided.
            - The function displays success or error messages depending on the outcome of the comment creation process.
            - If the form is invalid, the function renders the comment form template with the form and tag form objects.
        """
        form = CommentForm(request.POST)
        tag_form = CommentTagForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            post = get_object_or_404(Post, id=id)
            comment.user = request.user
            comment.post = post
            comment.save()
            if tag_form.is_valid():
                tag_name = tag_form.cleaned_data['name'].split(',')
                for name in tag_name:
                    name = name.strip()
                    tag, created = Tag.objects.get_or_create(name=name)
                    comment_tags = CommentTag.objects.create(comment=comment, tag=tag)
            messages.success(request, 'The comment has been created successfully.')
            return redirect('all-comments-for-post', id=post.id)
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/comment_form.html', {'form': form, 'id': id, 'tag_form': tag_form})


class EditCommentView(View):
    @method_decorator(login_required)
    def get(self, request, id, comment_id):
        """
        Retrieves a comment form for a specific post and comment.
        Args:
            request: The HTTP request object.
            id: The ID of the post.
            comment_id: The ID of the comment.
        Returns:
            A rendered comment form HTML page.
        Raises:
            Http404: If the post or comment does not exist.
        """
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == post.author or request.user == comment.user:
            context = {'form': CommentForm(instance=comment), 'id': id, 'comment_id': comment_id,
                'tag_form': PostTagForm(), 'comment_tags': post.tags.all()}
            return render(request, 'webapp/comment_form.html', context)

    @method_decorator(login_required)
    def post(self, request, id, comment_id):
        """
        This function is a POST request handler for updating a comment.
        Parameters:
            - request: The HTTP request object.
            - id: The ID of the post.
            - comment_id: The ID of the comment to be updated.
        Returns:
            - Redirects to the 'all-comments-for-post' view after updating the comment.
        This function is decorated with the 'login_required' decorator, which ensures that the user
        must be authenticated before accessing this view. It retrieves the post and comment objects
        based on the provided IDs. If the authenticated user is either the author of the post or the
        user who made the comment, it proceeds to update the comment using the provided form data.
        If the form is valid, it saves the comment and creates any new tags associated with it.
        Finally, it displays a success message and redirects the user to the 'all-comments-for-post'
        view for the corresponding post.
        If the form is invalid, it displays an error message and renders the 'comment_form.html'
        template with the appropriate form and context variables.
        """
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == post.author or request.user == comment.user:
            form = CommentForm(request.POST, instance=comment)
            tag_form = CommentTagForm(request.POST)
            if form.is_valid():
                form.save()
                if tag_form.is_valid():
                    tag_names = tag_form.cleaned_data['name'].split(',')
                    for name in tag_names:
                        name = name.strip()
                        tag, created = Tag.objects.get_or_create(name=name)
                        comment_tags = CommentTag.objects.create(comment=comment, tag=tag)
                messages.success(request, 'The comment has been updated successfully.')
                return redirect('all-comments-for-post', id=post.id)
            context = {'form': form, 'id': id, 'comment_id': comment_id, 'tag_form': tag_form}
            messages.error(request, 'Please correct the following errors:')
            return render(request, 'webapp/comment_form.html', context)


class DeleteCommentView(LoginRequiredMixin, View):
    def get(self, request, id, comment_id):
        """
        Get the comment confirmation delete page for a specific post and comment.
        Parameters:
            request (HttpRequest): The HTTP request object.
            id (int): The ID of the post.
            comment_id (int): The ID of the comment.
        Returns:
            HttpResponse: The rendered comment confirmation delete page.
        """
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)

        if request.user == post.author or request.user == comment.user:
            context = {'post': post}
            return render(request, 'webapp/comment_confirm_delete.html', context)

    def post(self, request, id, comment_id):
        """
        Deletes a comment from a post if the requesting user is either the author of the post or the author of the comment.
        Args:
            request (HttpRequest): The HTTP request object.
            id (int): The primary key of the post.
            comment_id (int): The primary key of the comment.
        Returns:
            HttpResponseRedirect: A redirect response to the view displaying all comments for the post.
        Raises:
            Http404: If the post or comment does not exist.
        """
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)

        if request.user == post.author or request.user == comment.user:
            comment.delete()
            messages.success(request, 'The comment has been deleted successfully.')
        return redirect('all-comments-for-post', id=post.id)
