import json
import boto3
import botocore.exceptions

from PIL import Image
import io
 
def lambda_handler(event, context):
    
    user = event['body']

    bucket='photosdcc'
    collectionId='mycollection'
    
    folder = 'photos/' + user + '/'
    fileName=folder + 'test.jpg'
    threshold = 90
    maxFaces=4
    nomi = []
     
    try:

        client=boto3.client('rekognition')
        s3 = boto3.client('s3')
    
        # Rileva i volti nell'immagine
        response = client.detect_faces(
            Image={'S3Object': {'Bucket': bucket, 'Name': fileName}},
            Attributes=['DEFAULT']
        )
        
        # Estrai i bounding box dei volti rilevati
        face_details = response['FaceDetails']
        bounding_boxes = [face['BoundingBox'] for face in face_details]
        
        
        local_file_path = '/tmp/locale.png'
        s3.download_file(bucket, fileName, local_file_path)
        image = Image.open(local_file_path)
      
        for bounding_box in bounding_boxes:
        
        
            # Calcola le coordinate del ritaglio
            width, height = image.size
            left = int(bounding_box['Left'] * width)
            top = int(bounding_box['Top'] * height)
            right = int((bounding_box['Left'] + bounding_box['Width']) * width)
            bottom = int((bounding_box['Top'] + bounding_box['Height']) * height)
            
            cropped_image = image.crop((left, top, right, bottom))
            
            buffer = io.BytesIO()
            cropped_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Converti il buffer in dati binari
            image_bytes = buffer.read()
            
            
            detect_face_response = client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['DEFAULT']
                )
            print(len(detect_face_response['FaceDetails']))
            if len(detect_face_response['FaceDetails']) >= 1:
                print("sono qui")
                response = client.search_faces_by_image(
                    CollectionId=collectionId,
                    Image={'Bytes': image_bytes},
                    FaceMatchThreshold=threshold,
                    MaxFaces=1
                )
                print(response)
                if response['FaceMatches']:
                    faceMatches = response['FaceMatches']
                    nomi.append(faceMatches[0]['Face']['ExternalImageId'])
                    print(nomi)
                else:
                    print("no")

            
        index = 1
        
        json_data = {}
        
        url = s3.generate_presigned_url('get_object',
                        Params={'Bucket': bucket, 'Key': fileName},
                        ExpiresIn=3600)
        
        for val in nomi:
            key = str(index)
            json_data[key] = val
            index += 1
        
        json_data['num'] = index - 1
        json_data['url'] = url 
                
        response = {
            'statusCode': 200,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            'body': json.dumps(json_data)
        }
        
        return response
        
    except Exception as e:
        
        print(e)
        
        return {
            'statusCode': 500,
            'headers': { 
                "Content-Type": "application/json",
                "access-control-allow-origin": "*",
                 'x-content-type-options': 'nosniff'
            },
            'body': json.dumps({'error': "Errore nel riconoscimento dei volti", 'exception': str(e)})
        }
    



