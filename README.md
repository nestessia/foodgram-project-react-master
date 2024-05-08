# Foodgram
![example workflow](https://github.com/nestessia/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Проект доступен по ссылке:
https://foodgram-nestessia.ddns.net/recipes 

## Стек
`Python` `Django` `JavaScript` `React` `API` `Nginx` `Docker-compose` `YAML`

## Описание
Foodgram - продуктовый помощник, платформа для публикации рецептов, которые можно добавлять в избранное и корзину для покупок. Также можно подписываться на других пользователей.

## Как развернуть локально
Клонировать репозиторий:
```
git clone git@github.com:nestessia/foodgram-project-react.git
```

Необходимо создать файл `.env`. Для этого в директории /infra выполните команду:
```
cp .env.exemple .env
```

Для работы проекта необходимо приложение Docker. В директории `/infra` выполните команды:
```
docker compose -f docker-compose.production.yml up
```

В другом терминале выполним миграции и загрузим данные.
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
```

Редок будет доступен по ссылке:
```
http://localhost/api/docs/
```
## Запуск на сервере (ОС Linux)
Создадим `.env`:
```
sudo nano .env
```

Добавим в него следующие переменные:
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=
SECRET_KEY=
ALLOWED_HOSTS=
```

Устанавливаем к Docker утилиту Docker Compose:
```
sudo apt update
sudo apt-get install docker-compose-plugin 
```

Создаем файл docker-compose.production.yml и копируем в него содержимое из репозитория

Запускаем проект, выполняем миграции и заполняем данными
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
```

## Примеры запросов к API
<details>
<summary> Получение и удаление токена </summary>
POST /api/auth/token/login/

POST /api/auth/token/logout/
</details>

<details>
<summary> Регистрация нового пользователя </summary>
POST /api/users/
</details>

<details>
<summary> Получение данных своей учетной записи </summary>
GET /api/users/me/
</details>

<details>
<summary> Получение страницы пользователя и списка всех пользователей </summary>
GET /api/users/id/

GET /api/users/?page=1&limit=3
</details>

<details>
<summary> Подписка и отписка </summary>
POST /api/users/id/subscribe/?recipes_limit=3

DELETE /api/users/id/subscribe/
</details>

<details>
<summary> Подписки пользователя </summary>
GET /api/users/subscriptions/
</details>

<details>
<summary> Получение рецепта и списка рецептов </summary>
GET /api/recipes/id/

GET /api/recipes/
</details>

<details>
<summary> Создание, обновление и удаление рецепта </summary>
POST /api/recipes/

PATCH /api/recipes/id/

DELETE /api/recipes/id/
</details>

<details>
<summary> Добавление и удаление избранных рецептов </summary>
POST /api/recipes/id/favorite/

DELETE /api/recipes/id/favorite/
</details>

<details>
<summary> Добавление и удаление рецептов из корзины покупок </summary>
POST /api/recipes/id/shopping_cart/

DELETE /api/recipes/id/shopping_cart/
</details>

<details>
<summary> Скачать список покупок </summary>
GET /api/recipes/download_shopping_cart/
</details>

## Автор
Анастасия Крючкова