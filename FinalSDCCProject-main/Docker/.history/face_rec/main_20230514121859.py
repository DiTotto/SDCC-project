import face_recognition as fr
import cv2
import numpy as np
import os
import pika
import json
import base64
import boto3
import urllib


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

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
# channel = connection.channel()
# channel.queue_declare(queue='coda_foto')
# channel.queue_declare(queue='coda_elaborati')
channel = None

def callback(ch, method, properties, body):
    filename=body.decode('utf-8')
    channel.basic_ack(delivery_tag=method.delivery_tag)
    #channel.queue_purge('coda_foto')
    # if method.delivery_tag != last_delivery_tag_processed + 1:
    #     #print("Delivery tag errato!")
    #     # out of order message, reject and requeue
    #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    # else:
    #     #print("Messaggio corretto!")
    #     # esegui le operazioni necessarie sul messaggio
    #     ch.basic_ack(delivery_tag=method.delivery_tag)
    #     # aggiorna il delivery tag dell'ultimo messaggio processato
    #     last_delivery_tag_processed = method.delivery_tag
    nomi = recognition(filename)

#----------------------------------------------
def rpc_callback(ch, method, props, body):
    # esegui il riconoscimento facciale come fai attualmente
    nomi = recognition(body.decode('utf-8'))

    # crea una nuova coda temporanea per la risposta
    result_queue = channel.queue_declare(queue='', exclusive=True)
    result_queue_name = result_queue.method.queue

    # imposta le proprietà del messaggio di risposta
    response = {
        'result': nomi
    }
    response_message = json.dumps(response)
    properties = pika.BasicProperties(
        correlation_id=props.correlation_id,
        content_type='application/json',
        reply_to=result_queue_name
    )

    # pubblica il messaggio di risposta sulla coda temporanea
    channel.basic_publish(exchange='',
                          routing_key=props.reply_to,
                          properties=properties,
                          body=response_message)

    # conferma la ricezione del messaggio sulla coda rpc
    channel.basic_ack(delivery_tag=method.delivery_tag)

#----------------------------------------------
#PRODUCER
def sendPhoto_to_rabbitmq(encoded_string):

    channel.basic_publish(exchange='', routing_key='coda_elaborati', body=encoded_string)
    connection.close()

def start_processing():

    global channel
    channel = connection.channel()
    channel.queue_declare(queue='coda_foto')
    channel.queue_declare(queue='coda_elaborati')
    channel.queue_declare(queue='coda_rpc')
    
    
    channel.basic_consume(queue='coda_rpc', on_message_callback=rpc_callback, auto_ack=False)
    channel.start_consuming()


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
    
    # Carica la foto su S3
    s3.put_object(Bucket=bucket_name, Key=folder_name + "test.jpg", Body=file_data)

    sendPhoto_to_rabbitmq("test.jpg")
    
    return nomi


if __name__ == '__main__':
    start_processing()
   



