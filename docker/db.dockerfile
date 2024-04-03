FROM postgres:15

RUN apt update && apt install -y postgresql-15-pgvector
