from flask import Flask, request, render_template, send_file, redirect, jsonify, url_for, session
import os
import pika
import json
from markupsafe import escape
import base64
import boto3
import urllib
import uuid
import atexit
from datetime import datetime
from flask_socketio import SocketIO

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['EDITED_FOLDER'] = 'static/edited'
app.secret_key = 'secretkey'


ACCESS_KEY_ID = None
ACCESS_KEY = None
SESSION_TOKEN = None
EMAIL = None
PASSWEMAIL = None
bucket_name = 'photosdcc'
folder_name = 'photos/'

s3 = None

# VARIABILE AMBIENTE PER I NOMI
app.config['NOMI'] = []

# ------------------CLASS----------------------------
class ServerRPCClass(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=3600))
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
            #body=str(n)
            body=n)
        self.connection.process_data_events(time_limit=None)
        return self.response
    

# ------------------END CLASS------------------------

# ------------------CLASS MAIL----------------------------
class MailRPCClass(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=3600))
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
            

    def call(self, dati):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_mail',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=dati)
        self.connection.process_data_events(time_limit=None)
        return self.response
    

# ------------------END CLASS------------------------

server_rpc = ServerRPCClass()
mail_rpc = MailRPCClass()

def cleanup():
    print("Cleaning up...")
    server_rpc.connection.close()
    mail_rpc.connection.close()

#PRODUCER
def sendPhoto_to_rabbitmq(dati):
    
    response = server_rpc.call(dati)
    app.config['NOMI'] = []
    for r in response:
        app.config['NOMI'].append(r)


#PRODUCER
def sendMail_to_rabbitmq(dati):
    resp = mail_rpc.call(dati)
    # controllare resp, gestire errori

def authenticate(aws_accesskey_id, aws_accesskey, aws_session_token, email_address, email_password):
    # Verifica le credenziali e autentica l'utente
    if aws_accesskey_id != None and  aws_accesskey != None and aws_session_token != None and email_address != None and email_password != None:
        session['authenticated'] = True
        return True
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    global ACCESS_KEY_ID
    global ACCESS_KEY
    global SESSION_TOKEN
    global EMAIL
    global PASSWEMAIL
    # Verifica le credenziali dell'utente
    if request.method == 'POST':
        # Controlla le credenziali e autentica l'utente
        authenticated = authenticate(request.form['aws_accesskey_id'], request.form['aws_accesskey'], request.form['aws_session_token'], request.form['email_address'], request.form['email_password'])
        if authenticated:
            ACCESS_KEY_ID = request.form['aws_accesskey_id']
            ACCESS_KEY = request.form['aws_accesskey']
            SESSION_TOKEN = request.form['aws_session_token']
            EMAIL = request.form['email_address']
            PASSWEMAIL = request.form['email_password']

            global s3
            if s3 == None:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=ACCESS_KEY,
                    aws_session_token=SESSION_TOKEN
                )

            # Reindirizza alla pagina home
            return redirect(url_for('home'))
        else:
            # Messaggio di errore per credenziali non valide
            error = 'Credenziali non valide. Riprova.'

    # Mostra il template della pagina di login
    return render_template('login.html', error=error)

@app.route('/home')
def home():
    # Verifica l'autenticazione dell'utente
    if not session.get('authenticated'):
        # Se l'utente non è autenticato, reindirizza alla pagina di login
        return redirect(url_for('login'))

    # Mostra il template della pagina home
    return render_template('index.html')


@app.route('/')
def index():
    return render_template('login.html') 

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
        

        global s3
        key = f"{folder_name}{filename}"
        # Carica la foto su S3
        s3.put_object(Bucket=bucket_name, Key=key, Body=file_data)

        #creo un JSON in cui inserire filename e credenziali di aws
        dati = {
            "filename": filename,
            "aws_accesskey_id": ACCESS_KEY_ID,
            "aws_accesskey": ACCESS_KEY,
            "aws_session_token": SESSION_TOKEN
        }

        # Converti i dati in formato JSON
        json_dati = json.dumps(dati)

        
        sendPhoto_to_rabbitmq(json_dati)
        return filename

@app.route('/images')
def images():
    nomi = []
    files = os.listdir(app.config['EDITED_FOLDER'])
    images = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    nomi = list(app.config['NOMI'])
    return jsonify({'immagini': images, 'nomi': nomi})

@app.route('/sendemail/<nome>', methods=['GET', 'POST'])
def send_email(nome):

    # Genera il link firmato per il file
    signed_url = s3.generate_presigned_url('get_object',
                    Params={'Bucket': bucket_name, 'Key': folder_name + 'test.jpg'},
                    ExpiresIn=3600)

    dati = {
        "nome": nome,
        "email_address": EMAIL,
        "email_password": PASSWEMAIL,
        "url": signed_url
    }

    json_dati = json.dumps(dati)

    sendMail_to_rabbitmq(json_dati)
    return redirect("/home")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)   
    #app.run(debug=True, host='0.0.0.0')

    atexit.register(cleanup)







