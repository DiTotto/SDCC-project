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

    try:
        
        
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
    
    
