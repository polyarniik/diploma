FROM python:3.10.10-bullseye

ENV DOCKER_DEFAULT_PLATFORM=linux/amd64
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.3.2

# Dockerize
# https://github.com/jwilder/dockerize#ubuntu-images
RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# System packages
RUN apt-get update -qq >/dev/null \
    && apt-get install -y \
    libpq-dev \
    python-dev \
    gcc \
    musl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip wheel \
    && pip install "poetry==$POETRY_VERSION"


COPY --chown=www-data:www-data pyproject.toml poetry.lock /var/app/
WORKDIR /var/app/
RUN poetry config virtualenvs.create false && poetry install --only docker
# RUN pip install -r /var/app/build/pip/dev_requirements.txt

VOLUME /var/app/
EXPOSE 8000
WORKDIR /var/app/src/

COPY --chown=www-data:www-data ci/dev/docker/backend/scripts/* /var/scripts/

RUN chmod +x /var/scripts/docker-entrypoint.sh
ENTRYPOINT ["/var/scripts/docker-entrypoint.sh"]
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
