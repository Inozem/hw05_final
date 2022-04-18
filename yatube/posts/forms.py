from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите текст поста'
        )
        self.fields['group'].empty_label = (
            'Выберите группу'
        )

    class Meta():
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите текст комментария'
        )

    class Meta():
        model = Comment
        fields = ('text',)
