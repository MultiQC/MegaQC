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
    apt-get install g++ -y && \

#Fix matplotlib being dumb
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/

#Link python
RUN ln -s /usr/bin/python2.7 /usr/bin/python  

# Install pip
RUN curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /opt/get-pip.py && \
    python /opt/get-pip.py && \
    rm /opt/get-pip.py

#Install Gunicorn
RUN pip install gunicorn

#Install MegaQC
#RUN pip install megaqc
RUN git clone https://github.com/ewels/MegaQC.git && python MegaQC/setup.py install

RUN megaqc initdb

RUN gunicorn megaqc.wsgi:app --timeout 300 &

EXPOSE 8000
