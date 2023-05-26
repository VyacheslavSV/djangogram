from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from webapp.models import UserProfile, Post, PostImage, Tag, PostTag, PostLike, Comment, CommentTag, CommentLike
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **options):
        fake = Faker()
        users = []
        for i in range(10):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            user = User.objects.create_user(
                username=username, email=email, password=password)
            users.append(user)
            UserProfile.objects.create(
                user=user,
                full_name=fake.name(),
                bio=fake.paragraph(),
                avatar=fake.image_url())
        for i in range(20):
            author = random.choice(users)
            post = Post.objects.create(
                author=author, caption=fake.text(
                    max_nb_chars=255), created_at=fake.date_time())
            for j in range(random.randint(1, 5)):
                PostImage.objects.create(post=post, image=fake.image_url())
            for j in range(random.randint(1, 3)):
                tag, created = Tag.objects.get_or_create(name=fake.word())
                PostTag.objects.create(post=post, tag=tag)
            for j in range(random.randint(1, 7)):
                user = random.choice(users)
                PostLike.objects.create(post=post, user=user)
        for i in range(30):
            user = random.choice(users)
            post = random.choice(Post.objects.all())
            comment = Comment.objects.create(
                user=user, post=post, content=fake.text())
            for j in range(random.randint(1, 3)):
                tag, created = Tag.objects.get_or_create(name=fake.word())
                CommentTag.objects.create(comment=comment, tag=tag)
            for j in range(random.randint(1, 10)):
                user = random.choice(users)
                CommentLike.objects.create(comment=comment, user=user)
        self.stdout.write(self.style.SUCCESS(
            'Successfully populated the database with fake data.'))
