FROM postgres


ENV POSTGRES_USER=${DB_USER}
ENV POSTGRES_PASSWORD=${DB_PASS}
ENV POSTGRES_DB=${DB_NAME}


COPY init.sql /docker-entrypoint-initdb.d/init.sql