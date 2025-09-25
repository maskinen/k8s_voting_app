FROM postgres:16-alpine
ENV POSTGRES_DB=vote POSTGRES_USER=postgres POSTGRES_PASSWORD=dev
COPY init.sql /docker-entrypoint-initdb.d/01_init.sql