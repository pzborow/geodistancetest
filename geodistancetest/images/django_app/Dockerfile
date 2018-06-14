FROM python:3.6

MAINTAINER Piotr Zborowski

ENV PYTHONUNBUFFERED 1


####  Update apt ####
RUN apt-get clean && \
    apt-key update && \
    apt-get -q -y update --fix-missing && \
    apt-get -q -y update


####  Locales  ####
# based on https://github.com/2xyo/docker-debian-locales/blob/master/conf/locale.gen
RUN apt-get install -q -y apt-utils && \
    apt-get install -q -y locales

ADD locale.gen /etc/locale.gen
RUN locale-gen && \
    locale-gen en_US.UTF-8 && \
    locale-gen pl_PL.UTF-8

ENV LANGUAGE pl_PL.UTF-8
ENV LANG pl_PL.UTF-8
ENV LC_ALL pl_PL.UTF-8
ENV LC_CTYPE pl_PL.UTF-8


#### Required system libraries ####
RUN apt-get install -q -y binutils libproj-dev gdal-bin
RUN apt-get install -q -y postgresql-client-common postgresql-client-9.4


#### Clear apt cache ####
RUN apt-get clean && \
    rm -r /var/lib/apt/lists/*


####  Install python ####
WORKDIR /srv
ADD requirements.txt /srv
RUN pip install -r requirements.txt


####  Adds some docker utilities  ####
# Based on https://github.com/geo-data/openstreetmap-tiles-docker/blob/master/Dockerfile
#
RUN mkdir -p /usr/local/share/doc/run
ADD help.txt /usr/local/share/doc/run/help.txt
ADD run.sh /usr/local/sbin/run
ENTRYPOINT ["/usr/local/sbin/run"]

#CMD ["help"] # Default to showing the usage text


# Define mountable directories.
VOLUME ["/srv"]
