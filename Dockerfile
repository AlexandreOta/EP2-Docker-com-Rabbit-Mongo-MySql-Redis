FROM python:3

ADD . /fila
WORKDIR /fila

COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh


RUN pip3 install -r requirements.txt






