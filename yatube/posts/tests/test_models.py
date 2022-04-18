from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    """Класс для проверки моделей приложения 'posts'."""

    @classmethod
    def setUpClass(cls):
        """Создание временной базы данных."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ' * 5,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        testing_object_titles = {
            group: group.title,
            post: post.text[:15],
        }
        for object, title in testing_object_titles.items():
            self.assertEqual(
                title,
                str(object),
                (
                    f'Класс "{object.__class__.__name__}" '
                    'имеет неправильное название'
                )
            )

    def test_verbose_names(self):
        """Проверяем, что у моделей верные verbose_name"""
        testing_object_verbose = {
            self.group: 'Группа публикаций',
            self.post: 'Публикация',
        }
        testing_object_fields_verbose = {
            self.group: {
                'title': 'Заголовок',
                'slug': 'Ссылка',
                'description': 'Описание',
            },
            self.post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа поста',
                'image': 'Изображение'
            }
        }
        for model, test_attributes in testing_object_fields_verbose.items():
            self.assertEqual(
                model._meta.verbose_name,
                testing_object_verbose[model],
                (
                    f'Для класса "{model.__class__.__name__}" '
                    'verbose_name задан неверно'
                )
            )
            for verbose, verbose_name in test_attributes.items():
                self.assertEqual(
                    model._meta.get_field(verbose).verbose_name,
                    verbose_name,
                    (
                        f'Для класса "{model.__class__.__name__}" '
                        f'атрибута "{verbose}" '
                        'verbose_name задан неверно'
                    )
                )
