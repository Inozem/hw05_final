from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post, User


class PostsViewsTests(TestCase):
    """Класс для проверки страниц view-функций приложения 'posts'"""

    @classmethod
    def setUpClass(cls):
        """Добавляем во временную базу данных
        обыекты пользователя, группы и поста."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post
        )
        cls.urls = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ),
            'post_create': reverse('posts:post_create'),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ),
        }

    def setUp(self):
        """Авторизуем автора поста."""
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsViewsTests.user)

    def post_context_test(self, response):
        """Функция для проверки контекста post"""
        test_post = response.context['post']
        self.assertEqual(test_post.id, self.post.id)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        self.assertEqual(test_post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """Проверяем какой как шаблон использует."""
        pattern_names_and_templates = {
            self.urls['index']: 'posts/index.html',
            self.urls['group_list']: 'posts/group_list.html',
            self.urls['profile']: 'posts/profile.html',
            self.urls['post_detail']: 'posts/post_detail.html',
            self.urls['post_create']: 'posts/create_post.html',
            self.urls['post_edit']: 'posts/create_post.html',
        }
        for pattern_name, template in pattern_names_and_templates.items():
            response = self.authorized_author.get(pattern_name)
            self.assertTemplateUsed(
                response,
                template,
                f'Ошибка в "{pattern_name}"'
            )

    def test_post_detail_show_correct_context(self):
        """Проверяем комментарий в контексте страницы post_detail."""
        response = self.authorized_author.get(self.urls['post_detail'])
        self.post_context_test(response)
        test_comment = response.context['comments'][0]
        self.assertEqual(test_comment.id, self.comment.id)
        self.assertEqual(test_comment.text, self.comment.text)
        self.assertEqual(test_comment.author, self.comment.author)
        self.assertEqual(test_comment.post, self.comment.post)

    def test_post_create_show_correct_context(self):
        """Проверяем контекст страницы post_create."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_author.get(self.urls['post_create'])
        form = response.context['form']
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Проверяем контекст страницы post_edit."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_author.get(self.urls['post_edit'])
        self.post_context_test(response)
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context['is_edit']
        self.assertIsInstance(is_edit, bool)
        self.assertEquals(is_edit, True)

    def test_post_on_pages(self):
        """Проверяем наличие поста и контекста на страницах:
        index, group_list, profile"""
        templates = (
            self.urls['index'],
            self.urls['group_list'],
            self.urls['profile'],
        )
        for template in templates:
            response = self.authorized_author.get(template)
            with self.subTest(template=template):
                self.post_context_test(response)


    def test_index_cach(self):
        """Проверяем сохраняются ли посты в кэш на главной странице"""
        response = self.authorized_author.get(self.urls['index'])
        content = response.content
        Post.objects.all().delete()
        self.assertEqual(len(Post.objects.all()), 0)
        new_content = response.content
        self.assertEquals(content, new_content)


class PaginatorPostViewsTest(TestCase):
    """Класс для проверки Paginator приложения posts."""
    NUMBER_OF_POSTS = 11
    NUMBER_OF_EXTRA_POSTS = 1
    SUM_OF_POSTS = NUMBER_OF_POSTS + NUMBER_OF_EXTRA_POSTS
    NUMBER_OF_POSTS_PER_PAGE = settings.POSTS_PER_PAGE

    @classmethod
    def setUpClass(cls):
        """Добавляем во временную базу данных обыекты:
        2 пользователя, 2 группы и 12 постов."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.user_2 = User.objects.create_user(username='author_2')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост №1',
            group=PaginatorPostViewsTest.group_1
        )
        number_of_posts = PaginatorPostViewsTest.NUMBER_OF_POSTS
        Post.objects.bulk_create(
            Post(
                author=cls.user_2,
                text=f'Тестовый пост №2_{i + 1}',
                group=PaginatorPostViewsTest.group_2
            ) for i in range(number_of_posts)
        )

    def setUp(self):
        """Авторизуем автора поста."""
        self.authorized_author = Client()
        self.authorized_author.force_login(PaginatorPostViewsTest.user)

    def test_index(self):
        """Проверяем количество постов на страницах index"""
        number_of_posts_per_page = (
            self.NUMBER_OF_POSTS_PER_PAGE,
            self.SUM_OF_POSTS - self.NUMBER_OF_POSTS_PER_PAGE,
        )
        for page_number in range(len(number_of_posts_per_page)):
            with self.subTest(page_number=page_number):
                page_url = reverse('posts:index') + f'?page={page_number + 1}'
                response = self.authorized_author.get(page_url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    number_of_posts_per_page[page_number],
                )

    def test_group_list(self):
        """Проверяем количество постов на страницах group_list
        и принадлежность всех постов одной группе"""
        number_of_posts_per_page = (
            self.NUMBER_OF_POSTS_PER_PAGE,
            self.NUMBER_OF_POSTS - self.NUMBER_OF_POSTS_PER_PAGE,
        )
        for page_number in range(len(number_of_posts_per_page)):
            with self.subTest(page_number=page_number):
                page_url = reverse(
                    'posts:group_list', kwargs={'slug': f'{self.group_2.slug}'}
                ) + f'?page={page_number + 1}'
                response = self.authorized_author.get(page_url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    number_of_posts_per_page[page_number],
                )
                for post in response.context['page_obj']:
                    self.assertEqual(
                        post.group.title,
                        self.group_2.title,
                        (
                            'Все посты должны принадлежать группе: '
                            f'{self.group_2.title}'
                        )
                    )

    def test_profile(self):
        """Проверяем количество постов на первой странице profile
        и принадлежность всех постов одному автору"""
        number_of_posts_per_page = (
            self.NUMBER_OF_POSTS_PER_PAGE,
            self.NUMBER_OF_POSTS - self.NUMBER_OF_POSTS_PER_PAGE,
        )
        for page_number in range(len(number_of_posts_per_page)):
            with self.subTest(page_number=page_number):
                page_url = reverse(
                    'posts:profile', kwargs={
                        'username': f'{self.user_2.username}'
                    }
                ) + f'?page={page_number + 1}'
                response = self.authorized_author.get(page_url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    number_of_posts_per_page[page_number],
                )
                for post in response.context['page_obj']:
                    self.assertEqual(
                        post.author.username,
                        self.user_2.username,
                    )


class FollowViewsTest(TestCase):
    """Класс для проверки подписок на авторов приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Добавляем во временную базу данных
        автризованных пользователя и автора, пост."""
        super().setUpClass()
        cls.client = User.objects.create_user(username='client')
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.follow = Follow.objects.create(
            user=cls.author,
            author=cls.client,
        )

    def setUp(self):
        """Создаем гостя и авторизуем автора и клиента."""
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewsTest.client)
        self.authorized_author = Client()
        self.authorized_author.force_login(FollowViewsTest.author)

    def test_following(self):
        """Проверяем возможность подписываться на авторов."""
        count_follows = Follow.objects.count()
        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}
        )
        self.authorized_client.get(url)
        self.assertEqual(Follow.objects.count(), count_follows + 1)
        follow = Follow.objects.last()
        self.assertEqual(follow.user, FollowViewsTest.client)
        self.assertEqual(follow.author, FollowViewsTest.author)

    def test_following_unfollowing(self):
        """Проверяем возможность отписываться от авторов."""
        count_follows = Follow.objects.count()
        url = reverse(
            'posts:profile_unfollow',
            kwargs={'username': FollowViewsTest.client}
        )
        self.authorized_author.get(url)
        self.assertEqual(Follow.objects.count(), count_follows - 1)

    def test_adding_followers(self):
        """Проверяем, что посты автора, на которого подписались
        - появились у только у подписавшегося."""
        count_of_posts = Post.objects.filter(author=self.author).count()
        users_and_counts = {
            self.authorized_client: count_of_posts,
            self.authorized_author: 0
        }
        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}
        )
        self.authorized_client.get(url)
        url = reverse('posts:follow_index')
        for user, count in users_and_counts.items():
            with self.subTest(user=user):
                self.assertEqual(
                    len(user.get(url).context['page_obj']),
                    count)

    def test_following_for_guests(self):
        """Проверяем, что неаворизованный пользователь не может подписаться"""
        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}
        )
        redirect_url = f'/auth/login/?next=/profile/{self.author}/follow/'
        response = self.guest.get(url)
        self.assertRedirects(response, redirect_url)
