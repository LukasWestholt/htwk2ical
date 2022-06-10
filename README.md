# deployment
rename .env.default to .env and config values in it.

pip freeze > requirements.txt

### info Django

run test server:

- python manage.py runserver
- python manage.py makemigrations myapp1
- python manage.py sqlmigrate myapp1 0001
- python manage.py check
- python manage.py migrate
- python manage.py collectstatic
- python manage.py collectstatic --clear

- django-admin makemessages -l en -i venv
- django-admin makemessages --all -i venv


- docker exec -t -i betterhtwk2ical_nginx_1 /bin/sh
- python manage.py collectstatic

docker-compose up -d --build
docker-compose exec django python manage.py migrate --noinput
docker-compose exec django python manage.py collectstatic --no-input --clear