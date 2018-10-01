FROM ubuntu:16.04
RUN apt-get update && apt-get install -y python2.7 python-pip python-dev python3 python3-pip python3-dev build-essential libssl-dev libffi-dev sudo git
RUN pip install virtualenv 'tox!=2.4.0,>=2.3' jenkinsapi
RUN useradd jenkins --shell /bin/bash --create-home --uid 500
RUN echo "jenkins ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
