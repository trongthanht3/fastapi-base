# FastAPI Template for LLMs

## Introduction

- FastAPI Template for fast building LLMs API using FastAPI and Langchain
- Support:
    - [x] FastAPI application
    - [x] Celery worker
    - [x] PostgreSQL
    - [x] pgAdmin
    - [x] RabbitMQ
    - [x] Redis

**Note**: This template is not ready for production.

## Documentation

- [FastAPI](https://fastapi.tiangolo.com/)

## Installation

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Requirements

Environment variables: copy from `.env.example` to `.env` and change the values.
```bash
cp .env.example .env
```

### Docker

You can run the following command to start the server:

```bash
docker-compose up -d
```

### Development

Development environment requires:
- [Python](https://www.python.org/) >= 3.9
- [Redis](https://redis.io/) >= 6
- [PostgreSQL](https://www.postgresql.org/) >= 13
- [Poetry](https://python-poetry.org/)

To start development environment, run the following command:

```shell
cd src
poetry install
``` 
```shell
# Please active Poetry virtual environment before running the following command
# Start celery worker
celery -A celeryApp.worker worker -l info -Q main-queue -c 1
```
**Note**: Windows require [gevent](https://pypi.org/project/gevent/) to run celery worker.
```shell
celery -A celeryApp.worker worker -l info -Q main-queue -c 1 -P gevent
```

```shell
python app/main.py
```

### Gitlab CI/CD
Please add these variables to Gitlab CI/CD:
- `CI_JOB_TOKEN`: Gitlab CI/CD job token
- `CI_PROJECT_NAME`: Gitlab project name
- `CI_REGISTRY`: Gitlab registry
- `DOCKER_IMAGE_BACKEND`: Docker image name for backend (eg: `registry.gitlab.com/username/project_name/backend`)
- `ENV_FILE_DEV` (File): Environment variables file for development (eg: `.env.dev`)
- `GIT_REPO`: Current git repository 
- `SSH_PRIVATE_KEY`: SSH private key that added to deployment server
- `SSH_SERVER`: Deployment server
- `SSH_USER`: Deployment user
- `STACK_NAME`: Docker stack name

With `.gitlab-ci.yml`, please change `services.command` to your registry server.
```yaml
...
services:
   - name: docker:dind
     alias: docker
     # Change insecure-registry to your registry
     command: ['--insecure-registry=<container registry server>']
...
```

## Endpoints

| Endpoint       | Method | Description |
|----------------| --- | --- |
| `/`            | GET | Hello world |
| `/api/v1/docs` | | Swagger UI |

## TODO
- [ ] Traefik
- [ ] Testing
- [ ] OAuth2

## Contributing

## License
- [LICENSE](LICENSE)