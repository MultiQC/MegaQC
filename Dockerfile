FROM debian:latest

LABEL authors="phil.ewels@scilifelab.se,denis.moreno@scilifelab.se" \
    description="Docker image running MegaQC"

# Install container-wide requrements
RUN apt-get update && apt-get install git -y && \
    apt-get install python2.7 -y && \
    apt-get install python2.7-dev -y && \
    apt-get install libyaml-dev -y && \
    apt-get install libffi-dev -y && \
    apt-get install libpng-dev -y && \
    apt-get install libfreetype6-dev -y && \
    apt-get install curl -y && \
    apt-get install gcc -y && \
    apt-get install g++ -y && \
    apt-get install apache2 -y

# Enable apache mod_proxy
RUN a2enmod proxy
RUN a2enmod proxy_http

# Overwrite apache config
RUN echo "<VirtualHost *:80> \n\
    ServerName megaqc \n\
    ProxyPass / http://127.0.0.1:8000/ \n\
    ProxyPassReverse / http://127.0.0.1:8000/ \n\
</VirtualHost>" > /etc/apache2/sites-enabled/000-default.conf

# Fix matplotlib being dumb
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/

# Link python
RUN ln -s /usr/bin/python2.7 /usr/bin/python

# Install pip
RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /opt/get-pip.py && \
    python /opt/get-pip.py && \
    rm /opt/get-pip.py

# Install PostgreSQL and psycopg2
RUN apt-get install postgresql-9.6 postgresql-server-dev-9.6 -y

# Set data directory
ENV PGDATA /usr/local/lib/postgresql

# Tell MegaQC to use postgres / psycopg2
ENV MEGAQC_PRODUCTION 1

# create the data directory
RUN mkdir $PGDATA
RUN chown postgres $PGDATA
# Start postgres
# Create the basic requirements
RUN su postgres -c "/usr/lib/postgresql/9.6/bin/initdb" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w start" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/createuser megaqc_user" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/createdb megaqc -O megaqc_user" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w stop"

# Install MegaQC
COPY . MegaQC
WORKDIR MegaQC
RUN python setup.py install

# Set up the Postgres SQL server
RUN su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w start" && \
    megaqc initdb && \
    su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w stop"

# Use volumes to persist logs and data
VOLUME ["/var/log/postgresql", "/usr/local/lib/postgresql"]

# Run the MegaQC server
EXPOSE 80
CMD su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w start" && \
    service apache2 start && \
    gunicorn megaqc.wsgi:app --timeout 300
