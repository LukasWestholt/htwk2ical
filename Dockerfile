#### BUILDER ####

# pull official base image
FROM python:3.10.4-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk add --no-cache libpq-dev build-base

# install dependencies
COPY ./requirements.txt.docker ./requirements.txt
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# install other dependencies
RUN apk add --no-cache npm
COPY ./package.json ./package-lock.json ./
RUN npm install

#### FINAL ####

# pull official base image
FROM python:3.10.4-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
WORKDIR $APP_HOME

# install dependencies
# libpq for postgres
# nodejs for lessc yuglify
RUN apk add --no-cache libpq nodejs
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
COPY --from=builder /usr/src/app/node_modules node_modules
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint.prod.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME
COPY ./.env.docker .env

# chown all the files to the app user
RUN chown -R app:app $APP_HOME
RUN chmod +x entrypoint.sh

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]