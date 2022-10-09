#!/usr/bin/env sh

set -e

sleep 5
# Ожидаем запуска postgres и keycloak
dockerize -timeout 5s -wait tcp://postgres:5432 -timeout 5s -wait tcp://rabbit:5672

# накатываем миграции
python manage.py migrate --noinput

# Запуск команды переданной из CMD/command
exec "$@"
