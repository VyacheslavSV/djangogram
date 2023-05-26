from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .forms import PostForm, PostImageForm, BioForm, CommentForm, PostTagForm, CommentTagForm, LoginForm, \
    RegisterForm, User
from .models import Post, UserProfile, Tag, Comment, PostTag, PostLike, CommentTag, CommentLike, Subscription


class SignUpView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'webapp/register.html', {'form': form})

    def post(self, request):
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
        if request.user.is_authenticated:
            return redirect('user-information')
        form = LoginForm()
        return render(request, 'webapp/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(
                    request, f'Hi {username.title()}, welcome back!')
                return redirect('posts')
        messages.error(request, f'Invalid username or password')
        return render(request, 'webapp/login.html', {'form': form})


class SingOutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, f'You have been logged out.')
        return redirect('login')


class SubscribeView(View):
    @method_decorator(login_required)
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if Subscription.objects.filter(user=request.user, subscribed_to=user):
            request.user.profile.subscriptions.remove(user)
            Subscription.objects.filter(user=request.user, subscribed_to=user).delete()
            is_subscribed = False
        else:
            request.user.profile.subscriptions.add(user)
            Subscription.objects.create(user=request.user, subscribed_to=user)
            is_subscribed = True
        response = {
            'is_subscribed': is_subscribed,
        }
        return JsonResponse(response)


class FeedView(View):
    def get(self, request):
        posts = Post.objects.get_feed_posts(request.user)
        context = {'posts': posts}
        return render(request, 'webapp/feed.html', context)


class HomeView(View):
    @method_decorator(login_required)
    def get(self, request):
        posts = Post.objects.all().prefetch_related('images', 'tags')
        context = {'posts': posts}
        return render(request, 'webapp/home.html', context)


class LikePostView(View):
    @method_decorator(login_required)
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user.is_authenticated:
            try:
                like = post.likes.get(user=request.user)
                like.delete()
                is_liked = False
            except PostLike.DoesNotExist:
                like = PostLike.objects.create(post=post, user=request.user)
                is_liked = True
            response = {
                'is_liked': is_liked,
                'likes_count': post.likes.count(),
            }
            return JsonResponse(response)


class LikeCommentView(View):
    @method_decorator(login_required)
    def post(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        post = get_object_or_404(Post, id=post_id)
        if request.user.is_authenticated:
            liked_comments = CommentLike.objects.filter(
                comment=comment, user=request.user)
            if liked_comments.exists():
                liked_comments.delete()
                is_liked = False
            else:
                CommentLike.objects.create(comment=comment, user=request.user)
                is_liked = True
            response = {
                'is_liked': is_liked,
                'likes_count': liked_comments.count(),
            }
            return JsonResponse(response)


class UserBioView(View):
    @method_decorator(login_required)
    def get(self, request):
        bio = UserProfile.objects.filter(user=request.user)
        context = {'bio': bio}
        if bio:
            return render(request, 'webapp/user_info.html', context)
        return redirect('user-bio-create')


class UserBioCreateView(View):
    @method_decorator(login_required)
    def get(self, request):
        context = {'form': BioForm()}
        return render(request, 'webapp/bio_user.html', context)

    @method_decorator(login_required)
    def post(self, request):
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
        queryset = UserProfile.objects.filter(user=request.user)

        post = get_object_or_404(queryset, pk=id)
        context = {'form': BioForm(instance=post), 'id': id}
        return render(request, 'webapp/bio_user.html', context)

    @method_decorator(login_required)
    def post(self, request, id):
        queryset = UserProfile.objects.filter(user=request.user)
        post = get_object_or_404(queryset, pk=id)
        form = BioForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'The bio has has been updated successfully.')
            return redirect('user-information')
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/bio_user.html', {'form': form})


class CreatePostView(View):
    @method_decorator(login_required)
    def get(self, request):
        context = {
            'form': PostForm(),
            'post_image_form': PostImageForm(),
            'tag_form': PostTagForm()}
        return render(request, 'webapp/post_form.html', context)

    @method_decorator(login_required)
    def post(self, request):
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
            messages.success(
                request, 'The post has been created successfully.')
            return redirect('posts')
        messages.error(request, 'Please correct the following errors:')
        return render(request,
                      'webapp/post_form.html',
                      {'form': form,
                       'post_image_form': post_image_form,
                       'tag_form': tag_form})


class EditPostView(View):
    @method_decorator(login_required)
    def get(self, request, post_id):
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {
            'form': PostForm(
                instance=post),
            'post_image_form': PostImageForm(
                instance=post.images.first()),
            'tag_form': PostTagForm(),
            'post_tags': post.tags.all()}
        return render(request, 'webapp/post_form.html', context)

    @method_decorator(login_required)
    def post(self, request, post_id):
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        form = PostForm(request.POST, instance=post)
        post_image_form = PostImageForm(
            request.POST, request.FILES, instance=post.images.first())
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
            messages.success(
                request, 'The post has been updated successfully.')
            return redirect('posts')
        context = {
            'form': form,
            'post_image_form': post_image_form,
            'tag_form': tag_form,
            'post_tags': post.tags.all()}
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/post_form.html', context)


class DeletePostView(View):
    @method_decorator(login_required)
    def get(self, request, post_id):
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {'post': post}
        return render(request, 'webapp/post_confirm_delete.html', context)

    @method_decorator(login_required)
    def post(self, request, post_id):
        queryset = Post.objects.filter(author=request.user)
        post = get_object_or_404(queryset, pk=post_id)
        context = {'post': post}
        post.delete()
        messages.success(request, 'The post has been deleted successfully.')
        return redirect('posts')


class AllCommentsForPostView(View):
    @method_decorator(login_required)
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        comments = Comment.objects.filter(post=post)
        context = {'post': post, 'comments': comments}
        return render(request, 'webapp/comments_post.html', context)


class CommentsForPostCreateView(View):
    @method_decorator(login_required)
    def get(self, request, id):
        context = {'form': CommentForm(), 'tag_form': CommentTagForm()}
        return render(request, 'webapp/comment_form.html', context)

    @method_decorator(login_required)
    def post(self, request, id):
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
                    comment_tags = CommentTag.objects.create(
                        comment=comment, tag=tag)
            messages.success(
                request, 'The comment has been created successfully.')
            return redirect('all-comments-for-post', id=post.id)
        messages.error(request, 'Please correct the following errors:')
        return render(request, 'webapp/comment_form.html',
                      {'form': form, 'id': id, 'tag_form': tag_form})


class EditCommentView(View):
    @method_decorator(login_required)
    def get(self, request, id, comment_id):
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == post.author or request.user == comment.user:
            context = {
                'form': CommentForm(
                    instance=comment),
                'id': id,
                'comment_id': comment_id,
                'tag_form': PostTagForm(),
                'comment_tags': post.tags.all()}
            return render(request, 'webapp/comment_form.html', context)

    @method_decorator(login_required)
    def post(self, request, id, comment_id):
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
                        comment_tags = CommentTag.objects.create(
                            comment=comment, tag=tag)
                messages.success(
                    request, 'The comment has been updated successfully.')
                return redirect('all-comments-for-post', id=post.id)
            context = {
                'form': form,
                'id': id,
                'comment_id': comment_id,
                'tag_form': tag_form}
            messages.error(request, 'Please correct the following errors:')
            return render(request, 'webapp/comment_form.html', context)


class DeleteCommentView(LoginRequiredMixin, View):
    def get(self, request, id, comment_id):
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)

        if request.user == post.author or request.user == comment.user:
            context = {'post': post}
            return render(request, 'webapp/comment_confirm_delete.html', context)

    def post(self, request, id, comment_id):
        post = get_object_or_404(Post, pk=id)
        comment = get_object_or_404(Comment, pk=comment_id)

        if request.user == post.author or request.user == comment.user:
            comment.delete()
            messages.success(request, 'The comment has been deleted successfully.')
        return redirect('all-comments-for-post', id=post.id)
