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
COPY *.py /

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/bin/sh", "-c", "python3 /main.py $INPUT_MOFE_USERNAME $INPUT_MOFE_PASSWORD --upload-testcases $INPUT_UPLOAD_TESTCASES --upload-statement $INPUT_UPLOAD_STATEMENT --force-upload-statement $INPUT_FORCE_UPLOAD_STATEMENT --use-debug-logging $INPUT_USE_DEBUG_LOGGING"]
