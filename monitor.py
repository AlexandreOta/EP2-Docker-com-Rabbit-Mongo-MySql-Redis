import os
from flask import Flask, redirect, url_for, request, render_template
import pymongo
from redis import Redis
import pymysql

client = pymongo.MongoClient("db_mongo")

db = client.LogsSenac

app = Flask(__name__)

def lista_usuarios():
    try:
        bd = pymysql.connect(   host='db_mysql',
                                user='root',
                                password='root',
                                db='DBSenac'
                            )
    except:
        print("Erro Mysql")
                            
    cursor = bd.cursor()
    cursor.execute('SELECT * FROM Usuarios')
    #results = cursor.fetchall()
    results = [[id, nome] for (id, nome) in cursor]
    cursor.close()
    bd.close()
    print(results)
    return results


@app.route('/')
def monitor():
    redis = Redis(host='db_redis', db=0, socket_connect_timeout=2, socket_timeout=2)

    _items = db.LogsSenac.find()
    items = [item for item in _items]
    usuarios=lista_usuarios()
    num_get=redis.get('inserts')
    if num_get is None:
        num_inserts=0        
    else:
        num_inserts=num_get.decode("utf-8")
    return render_template('monitor.html',usuarios=usuarios, items=items, num_inserts=num_inserts)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005,debug=True)


