FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pika

COPY gpioActor.py ./

CMD [ "python3", "./gpioActor.py" ]
