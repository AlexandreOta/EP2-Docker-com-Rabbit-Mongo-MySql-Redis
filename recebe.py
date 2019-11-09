#!/usr/bin/env python

import sys
import pika
import pymongo
from redis import Redis, RedisError
import pymysql
import datetime
import time
import socket


redis = Redis(host='db_redis', db=0, socket_connect_timeout=2, socket_timeout=2)

client = pymongo.MongoClient("db_mongo")
dbMongo = client.LogsSenac

    
## Tentativa de subir as filas
pingcounter = 0
isreachable = False
while isreachable is False and pingcounter < 2:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('rabbitmq', 15672))
        isreachable = True
    except socket.error as e:
        time.sleep(5)
        pingcounter += 1
    s.close()

if isreachable:
    #conecta no rabbit
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    #define uma exchange
    channel.exchange_declare(exchange='filas', exchange_type='fanout')

    #cria 3 filas de controle
    result = channel.queue_declare(queue='c1', exclusive=False)
    channel.queue_bind(exchange='filas', queue='c1')

    result = channel.queue_declare(queue='c2', exclusive=False)
    channel.queue_bind(exchange='filas', queue='c2')

    result = channel.queue_declare(queue='c3', exclusive=False)
    channel.queue_bind(exchange='filas', queue='c3')

#Logs no Mongo
def callback_c1(ch, method, properties, body):
    s=body.decode("utf-8")
    k=s.split(";")
    
    query = {
            'comando': k[0],
            'id': k[1],
            'nome': k[2],
            'data' : datetime.datetime.utcnow()
        }
    try:
        dbMongo.LogsSenac.insert_one(query)
    except:
        print("Erro de Mongo</i>")    

    print(query)

#contador no Redis
def callback_c2(ch, method, properties, body):
    s=body.decode("utf-8")
    
    k=s.split(";")
    if k[0]=='insert': 
        try:
            num_insert = redis.incr("inserts")
        except RedisError:
            print("<i>Erro de conexao Redis</i>")
    print(" Numero de inserts: " + str(redis.get('inserts')))
    

#Usuarios no MySql
def callback_c3(ch, method, properties, body):
    s=body.decode("utf-8")
    
    k=s.split(";")

    if k[0]=="insert" :
        query = "insert Usuarios (id,nome) values(" +  k[1] + ",'" + k[2] + "'); "
    elif k[0]=="delete" :
        query = "delete from Usuarios where id=" +  k[1] + ";"
    else:
        query = "update Usuarios set nome='" + k[2] + "' where id=" +  k[1] +";"

    print(query)    
    try:
        bd = pymysql.connect(host='db_mysql',
                             user='root',
                             password='root',
                             db='DBSenac')
    except:
        
        print("Erro na MySql Connect")
 
    cursor = bd.cursor()
    
    try:
        cursor.execute(query)
        bd.commit()
    except:
        bd.rollback()
        print("Erro na atualização de dados")
 
    # fecha a conexão
    bd.close()


def recebe_fila(fila):
    if fila=='c1':
        channel.basic_consume(queue=fila, on_message_callback=callback_c1, auto_ack=True)
    elif fila=='c2':
        channel.basic_consume(queue=fila, on_message_callback=callback_c2, auto_ack=True)
    else:
        channel.basic_consume(queue=fila, on_message_callback=callback_c3, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    recebe_fila(str(sys.argv[1]))

