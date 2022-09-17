### О проекте:

Yatube - это проект социальной сети с возможностью делать публикации, оставлять под ними комментарии и подписываться на авторов.
Для оптимизации работы проекта использовал кеширование списка публикаций на главной странице. Написал тесты через Unittest.
Стек: Django, Django REST framework, Simple JWT, SQLite


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Inozem/hw05_final.git
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:
```
cd yatube
python3 manage.py makemigrations
python3 manage.py migrate
```

Запустить проект:
```
python3 manage.py runserver
```

Автор проекта: Иноземцев Сергей
