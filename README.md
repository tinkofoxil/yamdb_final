![example workflow](https://github.com/tinkofoxil/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# INFRA_SP2

Цель работы над проектом - получить опыт работы с Docker.

## Описание

Проект **YaMDb** собирает **отзывы (Review)** пользователей на **произведения 
(Titles)**. 

Произведения делятся на категории: «Книги», «Фильмы», «Музыка». 
**Список категорий (Category)** может быть расширен администратором.

Произведению может быть присвоен **жанр (Genre)** из списка предустановленных.
Новые жанры может создавать только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые
**отзывы (Review)** и ставят произведению оценку (от одного до десяти).
Из пользовательских оценок формируется усреднённая оценка произведения — 
**рейтинг**.
На одно произведение пользователь может оставить только один отзыв.

Сами произведения в **YaMDb** не хранятся, здесь нельзя посмотреть фильм или 
послушать музыку.

## Настройка и запуск:
1. Настройка окружения:
   ```
   touch .env
   nano .env
   ```
   Заполнить по этому примеру:
   ```
   SECRET_KEY="SECRET_KEY" # секретный ключ проекта Django
   DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
   DB_NAME=postgres # имя базы данных
   POSTGRES_USER=postgres # логин для подключения к базе данных
   POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
   DB_HOST=db # название сервиса (контейнера)
   DB_PORT=5432 # порт для подключения к БД
   ```

2. Запуск приложения в контейнерах:
   ```
   docker-compose up -d --build
   ```
   
3. Наполнение базы данных:
   ```
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py loaddata fixtures.json
   docker-compose exec web python manage.py collectstatic --no-input
   ```