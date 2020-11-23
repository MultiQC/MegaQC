# Compile the JS in an isolated container
FROM node:latest
COPY . /app
WORKDIR /app
RUN npm install
RUN npm run build

# Setup the final container that will we run
FROM tiangolo/meinheld-gunicorn-flask:python3.8
LABEL authors="phil.ewels@scilifelab.se,denis.moreno@scilifelab.se" \
    description="Docker image running MegaQC with Gunicorn"

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
# Copy the compiled JS in from the other node container
COPY --from=0 /app/megaqc/static/ /app/megaqc/static/
RUN pip install /app[prod]
