from flask import Flask, redirect, url_for, request, render_template

import pika


app = Flask(__name__)

@app.route('/')
def envia():
    return render_template('envia.html')


def p_insert(id, nome):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.exchange_declare(exchange='filas', exchange_type='fanout')
    
    message =  "insert;" + id + ";" + nome
    channel.basic_publish(exchange='filas', routing_key='', body=message)
    print(" [x] Sent %r" % message)
    connection.close()

def p_delete(id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.exchange_declare(exchange='filas', exchange_type='fanout')

    
    message =  "delete;" + id + ";"
    channel.basic_publish(exchange='filas', routing_key='c1', body=message)
    print(" [x] Sent %r" % message)
    connection.close()

def p_update(id,nome):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.exchange_declare(exchange='filas', exchange_type='fanout')

    message =  "update;" + id + ";" + nome
    channel.basic_publish(exchange='filas', routing_key='c2', body=message)
    print(" [x] Sent %r" % message)
    connection.close()



@app.route('/insert',methods=['POST'])
def insert():
    p_insert(request.form['id_in'], request.form['nome_in'])
    return redirect(url_for('envia'))


@app.route('/update',methods=['POST'])
def update():
    p_update(request.form['id_up'], request.form['nome_up'])
    return redirect(url_for('envia'))


@app.route('/delete',methods=['POST'])
def delete():
    p_delete(request.form['id_de'])
    return redirect(url_for('envia'))







if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


