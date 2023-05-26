from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='posts'),
    path('feeds/', views.FeedView.as_view(), name='feed'),
    path('accounts/login/', views.SignInView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.SingOutView.as_view(), name='logout'),
    path('accounts/profile/', views.UserBioView.as_view(), name='user-information'),
    path('profiles/create', views.UserBioCreateView.as_view(), name='user-bio-create'),
    path('profiles/edit/<int:id>/', views.UserBioEditView.as_view(), name='user-edit'),
    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe'),
    path('like/<int:post_id>/', views.LikePostView.as_view(), name='like-post'),
    path('like/<int:post_id>/<int:comment_id>/', views.LikeCommentView.as_view(), name='like-comment'),
    path('posts/create', views.CreatePostView.as_view(), name='post-create'),
    path('posts/edits/<int:post_id>/', views.EditPostView.as_view(), name='post-edit'),
    path('posts/delete/<int:post_id>/', views.DeletePostView.as_view(), name='post-delete'),
    path('posts/<int:id>/comments/', views.AllCommentsForPostView.as_view(), name='all-comments-for-post'),
    path('posts/<int:id>/comments/create/', views.CommentsForPostCreateView.as_view(), name='comments-create'),
    path('posts/<int:id>/comments/edit/<int:comment_id>/', views.EditCommentView.as_view(), name='comments-edit'),
    path('posts/<int:id>/comments/delete/<int:comment_id>/', views.DeleteCommentView.as_view(), name='comments-delete'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
