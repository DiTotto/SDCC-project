import face_recognition as fr
import cv2
import numpy as np
import os
import json
import base64
import boto3
import urllib
import time
import grpc
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
from concurrent import futures
import pybreaker


ACCESS_KEY_ID = ''
ACCESS_KEY = ''
SESSION_TOKEN = ''
filename = ''
bucket_name = 'photosdcc'
folder_name = 'photos/'
folder_user = ''

circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=20)

s3 = None

path = "static/train/"

known_names = []
known_name_encodings = []

class UnaryService(pb2_grpc.ImageServiceServicer):
    def __init__(self):
        pass

    def UploadFile(self, request, context):
        global ACCESS_KEY_ID
        global ACCESS_KEY
        global SESSION_TOKEN
        global filename

        data = json.loads(request.json_data)
        ACCESS_KEY_ID = data['aws_accesskey_id']
        ACCESS_KEY = data['aws_accesskey']
        SESSION_TOKEN = data['aws_session_token']
        filename = data['filename']
        try:
            name = recognition(filename)
        except CircuitBreakerError as e:
            return {"status": 1}
        
        names_json = json.dumps(name)

        return pb2.Nomi(nomi=names_json)
        


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ImageServiceServicer_to_server(UnaryService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
   

@circuit_breaker
def recognition(filename):

    global s3
    try:
        if s3 == None:
            s3 = boto3.client(
                's3',
                aws_access_key_id=ACCESS_KEY_ID,
                aws_secret_access_key=ACCESS_KEY,
                aws_session_token=SESSION_TOKEN
            )
    except Exception as e:
        return {"status": 1}
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

    global folder_user
    folder_user = folder_name + ACCESS_KEY_ID + "/"

    try:
        s3.download_file(bucket_name, folder_user + filename,'test.jpg')
    except Exception as e:
        return {"status": 1}

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

    name = folder_user + "test.jpg"
    
    # Carica la foto su S3
    try:
        s3.put_object(Bucket=bucket_name, Key=folder_user + "test.jpg", Body=file_data)
    except Exception as e:
        return {"status": 1}
    
    return {"status": 0, "nomi": nomi}


if __name__ == '__main__':
    serve()
   



