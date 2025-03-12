# Container image that runs your code
FROM python:3.13-slim

USER root
RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

COPY requirements.txt /root/

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pip install -r /root/requirements.txt

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY main.py /main.py

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["python3", "/main.py"]
