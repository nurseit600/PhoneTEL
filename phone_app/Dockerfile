FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /tel_app

COPY requirements.txt /tel_app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


COPY . /tel_app/