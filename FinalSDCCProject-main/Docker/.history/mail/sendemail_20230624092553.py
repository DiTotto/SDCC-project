import smtplib, json
from email.message import EmailMessage
import time
import atexit
import grpc
import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2
from concurrent import futures
import boto3
import pybreaker


EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ''
AWS_ACCESS_KEY_ID = ''
AWS_ACCESS_KEY = ''
AWS_SESSION_TOKEN = ''
URL = ''

circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=20)

class UnaryService(pb2_grpc.EmailServiceServicer):
    def __init__(self):
        pass

    def SendEmail(self, request, context):
        global EMAIL_ADDRESS
        global EMAIL_PASSWORD
        global AWS_ACCESS_KEY_ID
        global AWS_ACCESS_KEY
        global AWS_SESSION_TOKEN
        global URL

        data = json.loads(request.json_address)
        EMAIL_ADDRESS = data['email_address']
        EMAIL_PASSWORD = data['email_password']
        AWS_ACCESS_KEY_ID = data['aws_accesskey_id']
        AWS_ACCESS_KEY = data['aws_accesskey']
        AWS_SESSION_TOKEN = data['aws_session_token']
        URL = data['url']
        nome = data['nome']
        try:
            response = send(nome)
        except Exception as e:
            return {"msg": "Error", "status": 1}
        response_json = json.dumps(response)

        return pb2.Response(response=response_json)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_EmailServiceServicer_to_server(UnaryService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

@circuit_breaker
def send(nome):

    global EMAIL_ADDRESS
    global EMAIL_PASSWORD

    try:

        dynamodb = boto3.resource('dynamodb', 
                                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                                aws_secret_access_key=AWS_ACCESS_KEY, 
                                aws_session_token=AWS_SESSION_TOKEN,
                                region_name='us-east-1')
        table = dynamodb.Table('mailAddress')
        query = table.get_item(Key={'NOME': nome}) 

        if 'Item' in query:
            item = query['Item']   
            indirizzo = item['mail']
        else:
            return {"msg": "Error", "status": 1}
    except Exception as e:
        return {"msg": "Error", "status": 1}

    msg = EmailMessage()
    msg['Subject'] = "Detected in a photo"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = indirizzo
    msg.set_content("Detected in a photo" + "\n" + URL)

    # send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return {"msg": "Error", "status": 1}
    return {"msg": "Email sent successfully", "status": 0}

if __name__ == '__main__':
    serve()
