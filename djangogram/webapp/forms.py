from django.forms import ModelForm
from .models import Post, PostImage, UserProfile, Comment, Tag
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class BioForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'bio', 'avatar']


class PostImageForm(ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['caption']


class PostTagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class CommentTagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
