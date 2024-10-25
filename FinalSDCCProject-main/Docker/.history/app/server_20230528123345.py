from flask import Flask, request, render_template, send_file, redirect, jsonify, url_for
import os
import pika
import json
from markupsafe import escape
import base64
import boto3
import urllib
import uuid

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['EDITED_FOLDER'] = 'static/edited'

# Definisci le credenziali per l'accesso ad S3
ACCESS_KEY_ID = 'ASIAQEZ3HMBUIKXNV2VX'
ACCESS_KEY = 'nZ4Uii4Y5mDi6UK+VAF8v9GRP8tNmnBhTZrttT1Q'
SESSION_TOKEN = 'FwoGZXIvYXdzEDMaDMFbZHjWsm1mpbfNnSK+AWlsLC+luP/SYWGlmsBUyjAQSzx820YkE1r8AYvPY3IRrgx0w78LNnAXByLbF2AZRXexiOYYxdy7Ptb8rhq4V4+7uIz0IUuOiJXHVU4nJHmZ81JYYfV9dnH2FUjK/QvpZc6xsU8e++cNYoMxpp71bd5E6LfiIsp03Bf+16hskFiP6hx3VE3kTJPmYIvVeBdn5eHLNXqSZe+sRoRkYqBGbyx1C6MtFqpwWcOWgh5oOM5iWCCz7vHl9AtZd6vUk20o68PMowYyLXIgrN5XIxChGYs9S3qrvf2ovm2Wh9zHwpICkM80wiPhEEE4eiWYtItXWRn2qA=='
bucket_name = 'photosdcc'
folder_name = 'photos/'
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_KEY,
    aws_session_token=SESSION_TOKEN
)

# VARIABILE AMBIENTE PER I NOMI
app.config['NOMI'] = []

# ------------------CLASS----------------------------
class ServerRPCClass(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if  self.corr_id == props.correlation_id:
            response_list = json.loads(body)
            self.response = response_list
            s3.download_file(bucket_name, folder_name + 'test.jpg', os.path.join(app.config['EDITED_FOLDER'],'test.jpg'))

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        self.connection.process_data_events(time_limit=None)
        return self.response
    

# ------------------END CLASS------------------------

# ------------------CLASS MAIL----------------------------
class MailRPCClass(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'), heartbeat=10)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if  self.corr_id == props.correlation_id:
            self.response = body
            #s3.download_file(bucket_name, folder_name + 'test.jpg', os.path.join(app.config['EDITED_FOLDER'],'test.jpg'))

    def call(self, name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_mail',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(name))
        self.connection.process_data_events(time_limit=None)
        return self.response
    

# ------------------END CLASS------------------------

server_rpc = ServerRPCClass()
mail_rpc = MailRPCClass()

#PRODUCER
def sendPhoto_to_rabbitmq(filename):
    #in response ci sarà i nomi di chi è dentro la foto
    response = server_rpc.call(filename)
    app.config['NOMI'] = []
    for r in response:
        app.config['NOMI'].append(r)
    #app.config['NOMI'] = response
    # controllare response, gestire errori

#PRODUCER
def sendMail_to_rabbitmq(name):
    resp = mail_rpc.call(name)
    # controllare resp, gestire errori

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    
    nomi = []
    if request.method == 'POST':
        #ciclo per eliminare tutto ciò che è contenuto nella cartella UPLOAD
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))       

        #ciclo per eliminare tutto ciò che è contenuto nella cartella EDITED
        for filename in os.listdir(app.config['EDITED_FOLDER']):
            file_path = os.path.join(app.config['EDITED_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #upload su S3
        #Carica la foto dal file system
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            file_data = f.read()
        
        # Carica la foto su S3
        s3.put_object(Bucket=bucket_name, Key=folder_name + filename, Body=file_data)
        
        sendPhoto_to_rabbitmq(filename)
        return filename

@app.route('/images')
def images():
    nomi = []
    files = os.listdir(app.config['EDITED_FOLDER'])
    images = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    #print(','.join(images))
    immagini = ','.join(images)
    nomi = list(app.config['NOMI'])
    return jsonify({'immagini': immagini, 'nomi': nomi})

@app.route('/sendemail/<nome>', methods=['GET', 'POST'])
def send_email(nome):
    sendMail_to_rabbitmq(nome)
    return redirect("/")
    #print(nome)
    # if request.method == 'POST':
    #     return redirect("/")
    # return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')







