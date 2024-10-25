import smtplib 
import json
from email.message import EmailMessage
import boto3

def lambda_handler(event, context):
    
    data = event['body']
    
    data_obj = json.loads(data)
    

    
    key = data_obj['key']
    nome = data_obj['name']
    url = data_obj['url']
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('mailAddress')
        
        response = table.get_item(Key={'NOME': nome})
        
        if 'Item' in response:
            item = response['Item']
            mailToSend = item['mail']

        
        else:
            response = {
                'statusCode': 500,
                'headers': { 
                    "Content-Type": "application/json",
                    "access-control-allow-origin": "*",
                     'x-content-type-options': 'nosniff'
                },
                'body': json.dumps({'error': "Errore nel recupero del nome dal database"})
        
            }
            return response
        
        
        print(key)
        
        table2 = dynamodb.Table('dataSDCC')
        response2 = table2.get_item(Key={'ACCESS_KEY_ID': key})
        
        if 'Item' in response2:
            item = response2['Item']
            email = item['email_address']
            passw = item['email_password']
        
        else:
            response = {
                'statusCode': 500,
                'headers': { 
                    "Content-Type": "application/json",
                    "access-control-allow-origin": "*",
                     'x-content-type-options': 'nosniff'
                },
                'body': json.dumps({'error': "Errore nell'inserimento dell'email dal database"})
        
            }
            return response
        
        
        msg = EmailMessage()
        msg['Subject'] = "Detected in a photo"
        msg['From'] = email
        msg['To'] = mailToSend
        msg.set_content("Detected in a photo" + "\n" + url)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, passw)
            smtp.send_message(msg)
        
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
        print(e) 
        error_message = "Errore nell'invio dell'email; " + str(e)
        return {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            'body': json.dumps({'error': error_message})
        }
        
