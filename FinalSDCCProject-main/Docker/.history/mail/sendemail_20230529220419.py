# import packages
# below packages are built-in - no need to install anything new!
# yupi :)
import smtplib, json
from email.message import EmailMessage
import pika
import time
import atexit

#connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
#channel = connection.channel()
#channel.queue_declare(queue='rpc_mail')

def start_processing():

    while True:
        try:
            connection = establish_connection()
            channel = connection.channel()
            channel.queue_declare(queue='rpc_mail')
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='rpc_mail', on_message_callback=callback)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connessione persa...")
            time.sleep(5)
    
    #channel.basic_qos(prefetch_count=1)
    #channel.basic_consume(queue='rpc_mail', on_message_callback=callback)
    #channel.start_consuming()

def establish_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=3600))
    return connection

def callback(ch, method, props, body):
    name=body.decode('utf-8')
    send("ciao", name)

    try:
        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=str(name))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except pika.exceptions.AMQPConnectionError:
        print("Connessione persa...")
        time.sleep(5)
        start_processing()





# set your email and password
# please use App Password
email_address = "sdccdmdt@gmail.com"
email_password = "ecfvmlqnrfqtedfb"
def send(text, nome):

    # Apriamo il file in modalità lettura
    with open('indirizzi.json', 'r') as file:
    # Carichiamo il contenuto del file in un oggetto JSON
        dati = json.load(file)

    # Creiamo un dizionario Python a partire dall'oggetto JSON
    dizionario = dict(dati)

    if nome in dizionario.keys():
        indirizzo = dizionario[nome]
        #print(indirizzo)
    else:
        #print("Il valore cercato non è presente nel dizionario.")
        indirizzo = email_address


    # create email
    #print(emailto)
    msg = EmailMessage()
    msg['Subject'] = "Email subject"
    msg['From'] = email_address
    msg['To'] = indirizzo
    msg.set_content(text)

    # send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)
    return 0

if __name__ == '__main__':
    start_processing()
