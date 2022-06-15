#!/bin/sh
# don't forget: git update-index --chmod=+x entrypoint.sh

if [ "$WAIT" = "1" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py init

exec "$@"
