### Описание проекта:

Yatube - это учебный проект курса "Python-разработчик" от Яндекс-Практикума, который представляет собой социальную сеть с возможностью публикации постов и подписки на авторов. Данная версия проекта реализована без API.

Автор: Ната Бутрина

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/hatecodinglovemoney/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект на локальном сервере:

```
python3 manage.py runserver
```
