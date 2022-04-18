from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    """Класс для проверки страниц приложения 'posts'"""

    @classmethod
    def setUpClass(cls):
        """Добавляем во временную базу данных
        обыекты пользователя, группы и поста."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='author2')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        """Для проверки доступа к старницам:
        1. Создаем неавторизованного пользователя;
        2. Создаем авторизованного пользователя;
        3. Авторизуем автора поста."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='client2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_author = PostsURLTests.user
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_author)

    def test_statuses_of_urls_for_guests(self):
        """Проверяем статусы страниц для неавторизованного пользователя."""
        urls_and_statuses = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user_author.username}/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/posts/0/': HTTPStatus.NOT_FOUND,
        }
        for page_url, page_status in urls_and_statuses.items():
            response = self.guest_client.get(page_url)
            self.assertEqual(
                response.status_code,
                page_status,
                (
                    f'У страницы "{page_url}" '
                    f'должен быть сатус "{page_status}"'
                )
            )

    def test_templates_of_urls_for_guests(self):
        """Проверяем шаблоны страниц для неавторизованного пользователя."""
        urls_and_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for page_url, template in urls_and_templates.items():
            response = self.guest_client.get(page_url)
            self.assertTemplateUsed(
                response,
                template,
                (
                    f'Для страницы "{page_url}" '
                    f'должен вызываться шаблон "{template}"'
                )
            )

    def test_redirect_urls_for_guests(self):
        """Проверяем редирект со страниц для неавторизованного пользователя."""
        urls_to_redirect = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': (
                f'/auth/login/?next=/posts/{self.post.id}/edit/'
            ),
            f'/profile/{self.user_author.username}/': (
                f'/auth/login/?next=/profile/{self.user_author.username}/'
            ),
        }
        for page_url, redirect_url in urls_to_redirect.items():
            with self.subTest(page_url=page_url):
                response = self.guest_client.get(page_url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_statuses_of_urls_for_users(self):
        """Проверяем статусы страниц для авторизованного пользователя."""
        urls_and_statuses = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/posts/0/': HTTPStatus.NOT_FOUND,
        }
        for page_url, page_status in urls_and_statuses.items():
            response = self.authorized_client.get(page_url)
            self.assertEqual(
                response.status_code,
                page_status,
                (
                    f'У страницы "{page_url}" '
                    f'должен быть сатус "{page_status}"'
                )
            )

    def test_templates_of_urls_for_user(self):
        """Проверяем шаблоны страниц для автора."""
        page_urls = ('/create/', f'/posts/{self.post.id}/edit/')
        template = 'posts/create_post.html'
        for page_url in page_urls:
            with self.subTest(page_url=page_url):
                response = self.authorized_author.get(page_url)
                self.assertTemplateUsed(response, template)

    def test_redirect_urls_for_user(self):
        """Проверяем редирект со страниц для авторизованного пользователя,
        но не автора."""
        page_url = f'/posts/{self.post.id}/edit/'
        redirect_url = f'/posts/{self.post.id}/'
        response = self.authorized_client.get(page_url, follow=True)
        self.assertRedirects(response, redirect_url)

    def test_statuses_of_urls_for_authors(self):
        """Проверяем статусы страниц для автора."""
        urls_and_statuses = {
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            '/posts/0/': HTTPStatus.NOT_FOUND,
        }
        for page_url, page_status in urls_and_statuses.items():
            response = self.authorized_author.get(page_url)
            self.assertEqual(
                response.status_code,
                page_status,
                (
                    f'У страницы "{page_url}" '
                    f'должен быть сатус "{page_status}"'
                )
            )
