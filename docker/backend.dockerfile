####### BASE STAGE #######
FROM python:3.10-slim AS python-base
# https://python-poetry.org/docs#ci-recommendations
RUN apt update && apt install -y postgresql-client bash openssl gcc g++ libncurses5-dev build-essential curl git libpq-dev && \
    apt clean
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME=/opt/poetry
# Tell Poetry where to place its cache and virtual environment
ENV PIP_NO_CACHE_DIR=1
# RUN pip install "poetry==$POETRY_VERSION"
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create true

####### BUILDER STAGE #######
FROM python-base as builder
WORKDIR /app
# Creating a virtual environment just for poetry and install it with pip
COPY ./src/poetry.lock ./src/pyproject.toml ./

RUN poetry config virtualenvs.in-project true && \
    poetry lock --no-update && \
    poetry install --only=main --no-root

####### FINAL STAGE #######
FROM python-base as final
WORKDIR /
ENV PYTHONPATH=/
COPY --from=builder /app/.venv ./.venv
COPY ./src/ .
RUN chmod +x backend-start.sh
RUN chmod +x prestart.sh
RUN apt install -y ninja-build

CMD ["bash", "backend-start.sh"]
