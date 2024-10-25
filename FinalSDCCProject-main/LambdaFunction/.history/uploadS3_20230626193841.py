import boto3
import json
import base64
from io import BytesIO

def lambda_handler(event, context):
    folder_name = 'photos/'
    bucket_name = 'photosdcc'
  
    try:
          
        data = event['body']
        data_obj = json.loads(data)
        
        key = data_obj['key']
        image64 = data_obj['image']
        base64_image = image64.replace('data:image/jpeg;base64,', '')
        image = base64.b64decode(base64_image)
        image_stream = BytesIO(image)
        
    except Exception as e:
        raise e
        # Gestisci eventuali errori e restituisci una risposta di errore
        return {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            #'body': str(e)
            'body': json.dumps({'error': "Errore nel recupero dei dati dal body", 'exception': e})
        }
    

    # Configura la connessione a DynamoDB
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table('dataSDCC')

    try:
        # Query per ottenere la tupla corrispondente all'ACCESS_KEY
        """response = table.get_item(Key={'ACCESS_KEY_ID': key})

        # Verifica se l'item è stato trovato nella tabella
        if 'Item' in response:
            item = response['Item']
            # Esempio di accesso ai valori dell'item
            aws_accesskey_id = item['ACCESS_KEY_ID']
            aws_accesskey = item['aws_accesskey']
            aws_session_token = item['aws_session_token']
            email_address = item['email_address']
            email_password = item['email_password']

            # Restituisci una risposta con i valori recuperati
            #return {
                #'statusCode': 200,
                #'body': {
                #    'aws_accesskey_id': aws_accesskey_id,
                #    'aws_accesskey': aws_accesskey,
                #    'aws_session_token': aws_session_token,
                #    'email_address': email_address,
                #    'email_password': email_password
                #}
            #}
        else:
            response = {
                'statusCode': 404,
                'headers': { 
                    "Content-Type": "application/json",
                    "access-control-allow-origin": "*",
                     'x-content-type-options': 'nosniff'
                }
        
            }
            # Se l'item non è stato trovato, restituisci una risposta di errore
            return response"""
        
        
        folder_user = folder_name + key + '/'
        s3 = boto3.client('s3')
        
        
        s3.put_object(Bucket=bucket_name, Key=folder_user)
        s3.put_object(Bucket=bucket_name, Key=folder_user + "test.jpg", Body=image_stream)
        
        # ----------- #
        
        response = {
            'statusCode': 200,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            }
        }
        
        
        return response
        
    except Exception as e:
        # Gestisci eventuali errori e restituisci una risposta di errore
        return {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            #'body': str(e)
            'body': json.dumps({'error': "Errore nell'inserimento dell'immagine nel bucket ", 'exception': e})
        }
    
    
