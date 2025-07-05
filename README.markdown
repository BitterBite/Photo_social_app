# PhotoSocial API

PhotoSocial — это REST API для социальной сети, где пользователи могут регистрироваться, создавать посты с текстом, изображениями и геолокацией, ставить лайки, оставлять комментарии и удалять свои посты. API построено на Django REST Framework с использованием JWT-аутентификации и документацией через Swagger UI (drf-spectacular).

## Основные возможности

- Регистрация и аутентификация пользователей (через Djoser и SimpleJWT).
- Создание, просмотр, редактирование и удаление постов (редактирование и удаление доступны только автору).
- Загрузка нескольких изображений к постам.
- Добавление и просмотр комментариев к постам.
- Поставка лайков.
- Привязка геолокации к постам с обратным геокодированием (через `geopy`).
- Документация API через Swagger UI.

## Требования

- Python 3.12+
- PostgreSQL
- Утилиты: `pip`, `virtualenv`

## Установка

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/yourusername/photosocial-api.git
   cd photosocial
   ```

2. **Создайте и активируйте виртуальное окружение**:

   ```bash
   python -m venv .env
   source .env/bin/activate  # Для Windows: .env\Scripts\activate
   ```

3. **Установите зависимости**:

   ```bash
   pip install -r requirements.txt
   ```

Список `requirements.txt`:

   ```
    django==5.2.1
    djangorestframework==3.16.0
    psycopg2-binary==2.9.10
    python-dotenv==1.1.0
    djoser==2.3.1
    geopy==2.4.1
    drf-nested-routers==0.94.2
    pillow==11.2.1
    djangorestframework_simplejwt==5.5.0
    drf_spectacular==0.28.0
   ```

## Настройка базы данных

1. **Установите PostgreSQL**:
   - Убедитесь, что PostgreSQL установлен и запущен на вашем сервере или локальной машине.
   - Создайте базу данных для приложения:

     ```bash
     createdb photosocial_db
     ```

2. **Настройте переменные окружения**:
   - Создайте файл `.env` в корне проекта (рядом с `manage.py`).
   - Добавьте следующие переменные для подключения к PostgreSQL:

     ```text
     DB_NAME=photosocial_db
     DB_USER=your_postgres_user
     DB_PASSWORD=your_postgres_password
     DB_HOST=localhost
     DB_PORT=5432
     ```

     - `DB_NAME`: Имя базы данных (например, `photosocial_db`).
     - `DB_USER`: Имя пользователя PostgreSQL.
     - `DB_PASSWORD`: Пароль пользователя PostgreSQL.
     - `DB_HOST`: Хост базы данных (обычно `localhost` для локальной разработки).
     - `DB_PORT`: Порт PostgreSQL (по умолчанию `5432`).
     

3. **Проверьте конфигурацию в `settings.py`**:
   - Убедитесь, что настройки базы данных в `settings.py` используют переменные из `.env`:

     ```python
     import os
     from pathlib import Path
     from dotenv import load_dotenv

     BASE_DIR = Path(__file__).resolve().parent.parent
     load_dotenv(BASE_DIR / '.env')

     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': os.getenv('DB_NAME'),
             'USER': os.getenv('DB_USER'),
             'PASSWORD': os.getenv('DB_PASSWORD'),
             'HOST': os.getenv('DB_HOST'),
             'PORT': os.getenv('DB_PORT'),
         }
     }
     ```

4. **Примените миграции**:
   - После настройки выполните миграции для создания таблиц:

     ```bash
     python manage.py migrate
     ```

5. **Проверка подключения**:
   - Убедитесь, что приложение подключается к базе данных, запустив сервер:

     ```bash
     python manage.py runserver
     ```

   - Если возникают ошибки подключения, проверьте значения в `.env` и доступность PostgreSQL.


6. **Создайте суперпользователя**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Создайте папку для медиа**:

   ```bash
   mkdir -p media/posts
   ```

## Запуск проекта

1. Запустите сервер разработки:

   ```bash
   python manage.py runserver
   ```

2. Откройте API по адресу: `http://127.0.0.1:8000`.
3. Документация API доступна по адресу: `http://127.0.0.1:8000/swagger/`.

## Использование API

### Аутентификация

1. **Регистрация**:
   - `POST /auth/users/`:
     ```bash
     curl -X POST http://127.0.0.1:8000/auth/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "password123"}'
     ```

2. **Получение JWT**:
   - `POST /auth/jwt/create/`:
     ```bash
     curl -X POST http://127.0.0.1:8000/auth/jwt/create/ \
     -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "password123"}'
     ```

     Ответ:

     ```json
     {
       "access": "eyJhbGciOiJIUzI1Ni...",
       "refresh": "..."
     }
     ```

3. **Авторизация в Swagger UI**:
   - В поле **Authorize** введите **только** токен `access` (без `Bearer`).

### Основные эндпоинты

- **Создание поста**:
  - `POST /api/posts/`:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/posts/ \
    -H "Authorization: Bearer <access_token>" \
    -F "text=Мой пост" \
    -F "images=@/path/to/image.jpg" \
    -F "location={\"name\": \"Moscow\", \"latitude\": 55.7539, \"longitude\": 37.6208}"
    ```

- **Удаление поста** (только автор):
  - `DELETE /api/posts/{id}/`:
    ```bash
    curl -X DELETE http://127.0.0.1:8000/api/posts/1/ \
    -H "Authorization: Bearer <access_token>"
    ```

- **Лайк поста**:
  - `POST /api/posts/{id}/like/`:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/posts/1/like/ \
    -H "Authorization: Bearer <access_token>"
    ```

- **Добавление комментария**:
  - `POST /api/posts/{post_id}/comments/`:
    ```bash
    curl -X POST http://127.0.0.1:8000/api/posts/1/comments/ \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"text": "Отличный пост!"}'
    ```

- **Список постов**:
  - `GET /api/posts/`:
    ```bash
    curl -X GET http://127.0.0.1:8000/api/posts/ \
    -H "Authorization: Bearer <access_token>"
    ```

## Тестирование

1. **Создайте пользователей**:
   - Зарегистрируйте `user1` и `user2` через `POST /auth/users/`.
2. **Протестируйте функционал**:
   - Создание поста `user1`.
   - Добавление комментария и лайка от `user2`.
   - Удаление поста `user1` (успех).
   - Попытка удаления поста `user2` (ошибка 403).
3. **Проверка через Swagger UI**:
   - Используйте интерфейс для тестирования всех эндпоинтов.

## Структура проекта

```
photosocial/
├── manage.py
├── DjangoProject/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── posts/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── home.html
├── media/
│   └── posts/
├── static/
├── .env
├── requirements.txt
└── README.md
```

## Устранение ошибок

- **401 Unauthorized**:
  - Проверьте токен (вводите только токен в Swagger UI).
  - Обновите токен через `POST /auth/jwt/create/`.
- **403 Forbidden**:
  - Убедитесь, что пользователь имеет право выполнять действие (например, только автор может удалить пост).
- **Ошибка геокодирования**:
  - Проверьте подключение к интернету и лимиты `geopy`.

## Контакты

- Автор: Юрий [bitterbite90@gmail.com](mailto:bitterbite90@gmail.com)
- Репозиторий: [https://github.com/BitterBite/Photo_social_app](https://github.com/yourusername/photosocial)
```