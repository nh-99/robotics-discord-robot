FROM python:3.8-slim

RUN pip install --upgrade pip

RUN apt update -y && apt install curl -y
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt update -y && apt install -y nodejs

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PATH="/home/worker/.local/bin:${PATH}"
RUN playwright install --with-deps firefox

COPY . /app

LABEL maintainer="Noah Howard <noah@nohowtech.com>" \
      version="1.0.0"

WORKDIR /app
CMD python main.py