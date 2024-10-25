import boto3
import json
 
def lambda_handler(event, context):
    # Recupera i dati dal corpo della richiesta
    #request_data = event['body']
    try:
        request_data = json.loads(event['body'])
        
        aws_accesskey_id = request_data.get('aws_accesskey_id')
        aws_accesskey = request_data.get('aws_accesskey')
        aws_session_token = request_data.get('aws_session_token')
        email = request_data.get('email_address')
        email_password = request_data.get('email_password')
        
    except Exception as e:
        raise e
    
        response = {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            'body': json.dumps({'error': "Errore nel recupero dei dati", 'exception': e})
        }
        return response
    

    
    try:
        
        # Configura la connessione a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('dataSDCC')
        
        # Crea un oggetto con i dati da inserire nella tabella DynamoDB
        item = {
            'ACCESS_KEY_ID': aws_accesskey_id,
            'aws_accesskey': aws_accesskey,
            'aws_session_token': aws_session_token,
            'email_address': email,
            'email_password' : email_password
        }
    
        # Inserisci l'oggetto nella tabella DynamoDB
        table.put_item(Item=item)
        
        # Restituisci una risposta di successo
        response = {
            'statusCode': 200,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
                #"Location": "https://main.dybz1dlmle682.amplifyapp.com/index.html"
            },
            #'body': 'OK'
            'body': json.dumps({'key': aws_accesskey_id})
        }
    
        return response
    except Exception as e:
        raise e
        
        #gestione errore nell'inserimento dei dati nel database
        # Restituisci una risposta di errore
        response = {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
                #"Location": "https://main.dybz1dlmle682.amplifyapp.com/index.html"
            },
            #'body': 'OK'
            'body': json.dumps({'error': "Errore nell'inserimento dei dati nel database", 'exception': e})
        }
        return response