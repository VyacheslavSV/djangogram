
План дій

1.	Створити в гіті новий проект.
2.	Імпортувати в пайчарм створений проект.
3.	Створення віртуального оточення.
4.	Створюємо новий Django проект з використанням команди django-admin startproject djangogram.
    Після створення проекту, ви повинні перейти до папки проекту за допомогою команди cd djangogram.
5.	Створюємо новий додаток в проекті за допомогою команди python manage.py startapp webapp.
6.	структура проекту(буде дописано)
    djangogramm /
        djangogramm /
            init__.py
            settings.py
            urls.py
            wsgi.py
        webapp /
            migrations/
            static/
            templates/
                webapp/
                    profile.html
                    post_create.html
                    post_detail.html
                    post_like.html
                    comment_create.html
                    comment_like.html
            __init__.py
             admin.py
    		 apps.py
    		 models.py
             management/
                __init__.py
                commands/
                    __init__.py
                    _fake_data.py
    		 tests.py
    		 urls.py
                /profiles/{user_id}/ виведення інформації про профіль користувача
                /posts/create створення нового поста
                /posts/{post_id}/ детальна інформація про пост
                /posts/{post_id}/likes/ обробка дії like/unlike для публікації
                /posts/{post_id}/comments/create має відображати форму
                /posts/{post_id}/comments/ має повертати список коментарів
                /comments/{comments_id}/likes/ -обробка дії коментаря like/unlike

    		 views.py
                UserProfileview
                CreatePostView
                POstDetailView
                PostlikeView
                CommentCreateView
                CommentLikeView

	    manage.py


7.	Встановіти необхідні пакети, та додати requirements.txt.


 1. djangorestframework
 2. django-extensions
 3. django-rest-swagger
 4. easy-thumbnails
 5. django-simple-history
 6. django-model-utils
 7. django-storages


8.	Створюємо моделі бази даних для користувачів, повідомлень та зображень.

class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/')

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

 Потім виконуємо міграції за допомогою команд python manage.py makemigrations, --> python manage.py migrate.
9.	Генеруємо фейкові данні для бази данних  та генеруємо міграціїї
________________________________________________________________
fake_data.py
pip install faker

from django.core.management.base import DaseCommand
from django.contrib.auth.models import User
from myapp.models import Photo
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(sself, *args, **kwargs):
        fake = Faker()
        users = []
        photos = []

    for i in range(10):
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        user.append(user)

    for i in range(50):
        photo = Photo.objects.create(
            title=fake.sentence(),
            description=fake.text(),
            user=random.choice(user),
            image='path/to/image.jpg'
        )
        photos.append(photo)

    self.stdout.write(self.style.SUCCESS('Successfully populated the database'))

________________________________________________________________

10.    Створюємо сторінки HTML-шаблони та views.py. Також налаштовуємо urls.py.
11.	 Додаємо функціональність збереження фото та генерацію міграцій
12.	 Додаємо арі для всих views за допомогою   django-rest-framework
13.	Деплоємо на сервер
14.	Тестуємо
