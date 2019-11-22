FROM tiangolo/meinheld-gunicorn-flask:python3.7

LABEL authors="phil.ewels@scilifelab.se,denis.moreno@scilifelab.se" \
    description="Docker image running MegaQC"


# Tell MegaQC to use postgres / psycopg2
ENV MEGAQC_PRODUCTION=1 \
    MEGAQC_SECRET="SuperSecretValueYouShouldReallyChange" \
    MEGAQC_CONFIG="" \
    APP_MODULE=megaqc.wsgi:app\
    DB_HOST="127.0.0.1" \
    DB_PORT="5432" \
    DB_NAME="megaqc" \
    DB_USER="megaqc" \
    DB_PASS="megaqcpswd"

COPY . /app

RUN python /app/setup.py install
