import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Класс для провеки форм приложения 'posts'"""

    @classmethod
    def setUpClass(cls):
        """Добавляем во временную базу данных пользователя."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Авторизуем пользователя и создаем гостя."""
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(PostCreateFormTests.user)

    def test_creating_and_editing_post(self):
        """Проверяем создание и редактирование нового поста пользователями."""
        form_data_group = (self.group.pk, self.group_2.pk)
        urls = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for i in range(len(urls)):
            posts_count = Post.objects.count()
            with self.subTest(url=urls[i]):
                form_data = {
                    'text': 'Текст из формы',
                    'group': form_data_group[i],
                    'image': uploaded,
                }
                self.authorized_author.post(
                    urls[i],
                    data=form_data,
                    follow=True
                )
                self.assertEqual(
                    Post.objects.count(),
                    posts_count + 1 - i,
                )
                self.post.refresh_from_db()
                last_post = Post.objects.last()
                self.assertEquals(last_post.author, self.post.author)
                self.assertEquals(last_post.text, self.post.text)
                self.assertEquals(last_post.group, self.post.group)
                self.assertEquals(last_post.image, self.post.image)

    def test_editing_and_creating_post_by_guest(self):
        """Проверяем может ли гость создавать и редактировать посты."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.pk,
        }
        expected_results = {
            self.guest_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            ): reverse('users:login') + '?next=/create/',
        }
        for response, redirect in expected_results.items():
            with self.subTest(response=response):
                self.assertRedirects(response, redirect)
                self.assertEqual(Post.objects.count(), posts_count)

    def test_creating_coments_by_guest(self):
        """Проверяем может ли гость оставлять комментарии."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('users:login')
                             + f'?next=/posts/{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_creating_coments_by_client(self):
        """Проверяем может ли пользователь оставлять комментарии."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.last()
        self.assertEquals(last_comment.text, form_data['text'])
        self.assertEqual(Comment.objects.count(), comments_count + 1)
