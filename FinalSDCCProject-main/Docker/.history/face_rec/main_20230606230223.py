import face_recognition as fr
import cv2
import numpy as np
import os
import pika
import json
import base64
import boto3
import urllib
import time
import atexit


# Definisci le credenziali per l'accesso ad S3
ACCESS_KEY_ID = ''
ACCESS_KEY = ''
SESSION_TOKEN = ''
bucket_name = 'photosdcc'
folder_name = 'photos/'
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_KEY,
    aws_session_token=SESSION_TOKEN
)

path = "static/train/"

known_names = []
known_name_encodings = []

def start_processing():

    while True:
        try:
            connection = establish_connection()
            channel = connection.channel()
            channel.queue_declare(queue='rpc_queue')
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='rpc_queue', on_message_callback=callback)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connessione persa...")
            time.sleep(5)
    
    #channel.basic_qos(prefetch_count=1)
    #channel.basic_consume(queue='rpc_queue', on_message_callback=callback)
    #channel.start_consuming()

def establish_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=3600))
    return connection

def cleanup():
    connection = establish_connection()
    print("Closing connection...")
    connection.close()

#connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
#channel = connection.channel()
#channel.queue_declare(queue='rpc_queue')

def callback(ch, method, props, body):

    global ACCESS_KEY_ID
    global ACCESS_KEY
    global SESSION_TOKEN

    #filename=body.decode('utf-8')
    json_dati = json.loads(body)
    ACCESS_KEY_ID = json_dati['aws_accesskey_id']
    ACCESS_KEY = json_dati['aws_accesskey']
    SESSION_TOKEN = json_dati['aws_session_token']
    filename = json_dati['filename']
    name = recognition(filename)

    names_json = json.dumps(name)

    try:
        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=names_json)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except pika.exceptions.AMQPConnectionError:
        print("Connessione persa...")
        time.sleep(5)
        start_processing()


def recognition(filename):
    images = os.listdir(path)
    
    #ciclo per imparare i volti
    for _ in images:
        #print(path + _)
        if not _.startswith('.'):
            image = fr.load_image_file(path + _)
            image_path = path + _
            encoding = fr.face_encodings(image)[0]
            
            #print(encoding)

            known_name_encodings.append(encoding)
            known_names.append(os.path.splitext(os.path.basename(image_path))[0].capitalize())
    
    nomi = []
    s3.download_file(bucket_name, folder_name + filename,'test.jpg')
    image = cv2.imread("test.jpg")

    face_locations = fr.face_locations(image)
    face_encodings = fr.face_encodings(image, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = fr.compare_faces(known_name_encodings, face_encoding)
        name = ""

        face_distances = fr.face_distance(known_name_encodings, face_encoding)
        best_match = np.argmin(face_distances)

        if matches[best_match]:
            name = known_names[best_match]
            if (name not in nomi):
                nomi.append(name)
        
        
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(image, (left, bottom - 60), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left + 6, bottom - 6), font, 3.0, (255, 255, 255), 2)

    cv2.imwrite("test.jpg", image)

    #upload su S3
    #Carica la foto dal file system
    with open("test.jpg", 'rb') as f:
        file_data = f.read()

    name = folder_name + "test.jpg"
    
    # Carica la foto su S3
    s3.put_object(Bucket=bucket_name, Key=folder_name + "test.jpg", Body=file_data)
    
    return nomi


if __name__ == '__main__':
    start_processing()

    atexit.register(cleanup)
   



