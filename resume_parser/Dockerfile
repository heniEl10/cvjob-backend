FROM python:3.8
ENV PYTHONUNBUFFERED 1

# Set work directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    netcat-openbsd

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Copy application code
COPY . /usr/src/app

# Install Python dependencies
RUN pip install -r /usr/src/app/requirements.txt

# Install spaCy and spaCy models
RUN pip install spacy==2.3.5

# Run pre-requisite scripts and migrations
RUN python /usr/src/app/pre_requisites.py
#RUN python /usr/src/app/manage.py migrate
#RUN python /usr/src/app/manage.py collectstatic --no-input
