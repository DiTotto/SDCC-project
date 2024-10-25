from flask import Flask, request, render_template, redirect, jsonify, url_for
import os
import json
from markupsafe import escape
import base64
import boto3
import urllib
import grpc
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
import pybreaker

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['EDITED_FOLDER'] = 'static/edited'
app.secret_key = 'secretkey'
# VARIABILE AMBIENTE PER I NOMI
app.config['NOMI'] = []
app.config['signed_url'] = None

bucket_name = 'photosdcc'
folder_name = 'photos/'
folder_user = ''

s3 = None

# Create a circuit breaker object
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=20)

class UnaryClient(object):
    def __init__(self):
        self.host = 'face-rec-service.default.svc.cluster.local'
        #self.host = 'face-rec'
        self.port = 50051
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.port))
        self.stub = pb2_grpc.ImageServiceStub(self.channel)

    def ImageProcess(self, jsondata):
        data = self.stub.UploadFile(pb2.JsonDati(json_data=jsondata))
        listnomi = json.loads(data.nomi)
        return listnomi

class UnaryClientEmail(object):
    def __init__(self):
        self.host = 'mail-service.default.svc.cluster.local'
        #self.host = 'mail'
        self.port = 50052
        self.channel = grpc.insecure_channel('{}:{}'.format(self.host, self.port))
        self.stub = pb2_grpc.EmailServiceStub(self.channel)

    def EmailSend(self, jsondata):
        data = self.stub.SendEmail(pb2.JsonAddress(json_address=jsondata))
        response = json.loads(data.response)
        return response
    

# ------------------ROUTES----------------------------

def delete_folder():
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


@app.route('/close', methods=['GET'])
def handle_close():
    app.config['NOMI'] = None

@app.route('/home', methods=['GET','POST'])
def home():
    return render_template('index.html')


@app.route('/')
def index():
    delete_folder()
    return render_template('login.html') 

@app.route('/upload', methods=['POST'])
@circuit_breaker
def upload_file():

    data = request.json
    aws_accesskey_id = data.get('aws_accesskey_id')
    aws_accesskey = data.get('aws_accesskey')
    aws_session_token = data.get('aws_session_token')
    email_address = data.get('email_address')
    email_password = data.get('email_password')

    if request.method == 'POST':

        delete_folder()
        
        file_64 = data.get('file')
        base64_image = file_64.replace('data:image/jpeg;base64,', '')
        file = base64.b64decode(base64_image)
        filename = "test.jpg"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(file)

        #upload su S3
        #Carica la foto dal file system
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            file_data = f.read()


        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_accesskey_id,
            aws_secret_access_key=aws_accesskey,
            aws_session_token=aws_session_token
        )

        folder_user = folder_name + aws_accesskey_id + '/'

        key = f"{folder_user}{filename}"

        try:
            s3.put_object(Bucket=bucket_name, Key=key, Body=file_data)
        except Exception as e:
            print(e)
            return redirect(url_for('home'))

        #global URL
        #genero un url firmato per la foto appena caricata
        try:
            app.config['signed_url'] = s3.generate_presigned_url('get_object',
                        Params={'Bucket': bucket_name, 'Key': folder_user + 'test.jpg'},
                        ExpiresIn=3600)
        except Exception as e:
            print(e)
            return redirect(url_for('home'))

        dati = {
            "filename": filename,
            "aws_accesskey_id": aws_accesskey_id,
            "aws_accesskey": aws_accesskey,
            "aws_session_token": aws_session_token
        }

        # Converti i dati in formato JSON
        json_dati = json.dumps(dati)

        
        #sendPhoto_to_rabbitmq(json_dati)

        result = client.ImageProcess(json_dati)

        result_data = result

        if(result_data['status'] == 1):
            return redirect(url_for('home'))

        names = result_data['nomi']

        try:
            app.config['NOMI'] = []
            for r in names:
                app.config['NOMI'].append(r)

            s3.download_file(bucket_name, folder_user + 'test.jpg', os.path.join(app.config['EDITED_FOLDER'],'test.jpg'))
        except Exception as e:
            return redirect(url_for('home'))

        return redirect(url_for('home'))

@app.route('/images')
def images():

    nomi = []
    files = os.listdir(app.config['EDITED_FOLDER'])
    images = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    nomi = list(app.config['NOMI'])
    return jsonify({'immagini': images, 'nomi': nomi})

@app.route('/sendemail', methods=['POST'])
@circuit_breaker
def send_email():

    data = request.json
    aws_accesskey_id = data.get('aws_accesskey_id')
    aws_accesskey = data.get('aws_accesskey')
    aws_session_token = data.get('aws_session_token')
    email_address = data.get('email_address')
    email_password = data.get('email_password')
    nome = data.get('nome')


    if app.config['signed_url'] is not None:

        dati = {
            "nome": nome,
            "email_address": email_address,
            "email_password": email_password,
            "aws_accesskey_id": aws_accesskey_id,
            "aws_accesskey": aws_accesskey,
            "aws_session_token": aws_session_token,
            "url": app.config['signed_url']
        }

        json_address = json.dumps(dati)

        result = clientmail.EmailSend(json_address)

        jsondata = result

        if(jsondata['status'] == 1):
            return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
    
    else:
        return redirect(url_for('home'))


@app.route('/health-check')
def health_check():
    return 'OK'



if __name__ == '__main__':
    client = UnaryClient()
    clientmail = UnaryClientEmail()
    app.run(host='0.0.0.0', port=5000)

    







