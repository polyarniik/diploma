FROM python:3.10.10-bullseye

ENV DOCKER_DEFAULT_PLATFORM=linux/amd64
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.4.0

# Dockerize
# https://github.com/jwilder/dockerize#ubuntu-images
RUN apt-get update && apt-get install -y wget

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# System packages
RUN apt-get update -qq >/dev/null
RUN apt-get install -y \
    libpq-dev \
    python-dev \
    gcc \
    musl-dev \
    && pip install -U pip wheel \
    && pip install "poetry==$POETRY_VERSION"


# PDF2DOCX packages
RUN apt-get install ffmpeg libsm6 libxext6  -y

# PDF2IMAGE
RUN apt-get install -y poppler-utils

# TESSERACT OCR
RUN apt-get install -y tesseract-ocr libtesseract-dev

# LIBBREOFFICE
RUN apt-get install -y \
    libreoffice \
    openjdk-11-jre \
    libreoffice-java-common

RUN rm -rf /var/lib/apt/lists/*

COPY --chown=www-data:www-data pyproject.toml poetry.lock /var/app/
WORKDIR /var/app/
RUN poetry config virtualenvs.create false && poetry install --only main

VOLUME /var/app/
EXPOSE 8000
WORKDIR /var/app/src/

COPY --chown=www-data:www-data ci/dev/docker/backend/scripts/* /var/scripts/

RUN chmod +x /var/scripts/docker-entrypoint.sh
ENTRYPOINT ["/var/scripts/docker-entrypoint.sh"]
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
