FROM debian:latest

LABEL authors="phil.ewels@scilifelab.se,denis.moreno@scilifelab.se" \
    description="Docker image running MegaQC"

# Install container-wide requrements gcc, pip, zlib, libssl, make, libncurses, fortran77, g++, R
RUN apt-get update && apt-get install git -y && \
    apt-get install python2.7 -y && \
    apt-get install python2.7-dev -y && \
    apt-get install libffi-dev -y && \
    apt-get install libpng-dev -y && \
    apt-get install libfreetype6-dev -y && \
    apt-get install curl -y && \
    apt-get install gcc -y && \
    apt-get install g++ -y 

#Fix matplotlib being dumb
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/

#Link python
RUN ln -s /usr/bin/python2.7 /usr/bin/python  

# Install pip
RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /opt/get-pip.py && \
    python /opt/get-pip.py && \
    rm /opt/get-pip.py

#Install PostreSQL
RUN apt-get install postgresql-9.6 postgresql-server-dev-9.6 -y

#Set data directory : 
ENV PGDATA /usr/local/lib/postgresql

#create the data directory
RUN mkdir $PGDATA
RUN chown postgres $PGDATA
#Start postgres
#Create the basic requirements
RUN su postgres -c "/usr/lib/postgresql/9.6/bin/initdb" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w start" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/createuser megaqc_user" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/createdb megaqc -O megaqc_user" && \
su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w stop" 
#Install Gunicorn
RUN pip install gunicorn

#Install MegaQC
#RUN pip install megaqc
RUN git clone "https://galithil:########@github.com/ewels/MegaQC.git" && cd MegaQC && git checkout denis && python setup.py install



RUN su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w start" && \
megaqc initdb && \
su postgres -c "/usr/lib/postgresql/9.6/bin/pg_ctl -D $PGDATA -w stop" 

EXPOSE 8000
CMD gunicorn megaqc.wsgi:app --timeout 300

