
#FROM centos:8
FROM ubuntu:18.04

#RUN dnf install python36 python3-devel gcc -y
ENV DEBIAN_FRONTEND=noninteractive  
RUN apt-get update && apt-get install -y software-properties-common

RUN apt-get install -y \
    python3.6 \
    python3-pip

RUN apt-get install curl -y

COPY req.txt ./
RUN  pip3 install -r req.txt

RUN apt-get install software-properties-common &&  add-apt-repository ppa:certbot/certbot &&  apt-get update &&  apt-get install -y  python-certbot-nginx

#RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb
#RUN dpkg -i /chrome.deb || apt-get install -yf
#RUN rm /chrome.deb
RUN apt-get install -y chromium-browser 
#RUN apt-get install -y libglib2.0-0=2.50.3-2 \
#    libnss3=2:3.26.2-1.1+deb9u1 \
#    libgconf-2-4=3.2.6-4+b1 \
#    libfontconfig1=2.11.0-6.7+b1


WORKDIR /app
#RUN  pip3 install -r req.txt
 
#RUN yum apt-get install software-properties-common
# Copy the current directory contents into the container at /app 
ADD . /app
#RUN  pip3 install -r req.txt

COPY ventures-307500-b224edc160d6.json /app

RUN mkdir -p /app/ssl-folder && chown -R root:root /app/ssl-folder

#SHELL ["/bin/bash"]
#RUN yum  apt-get install software-properties-common  && yum  add-apt-repository ppa:certbot/certbot  && yum  apt-get update  && yum  apt-get install python-certbot-nginx

#RUN yum apt-get install software-properties-common 

#RUN  pip3 install -r req.txt


# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]

