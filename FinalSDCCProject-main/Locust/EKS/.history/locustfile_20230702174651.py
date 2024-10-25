from locust import HttpUser, task, between, TaskSet
import json
import time
import base64


class UserLogin(HttpUser):

    wait_time = between(23, 38) 

    @task(4)
    def userTest(self):

        

        response = self.client.get('/')
        if(response.status_code != 200):
            print("Error in get")

class RecognitionUser(HttpUser):
    
     wait_time = between(23, 38) 
     @task
     def userTest(self):
        headersFile = {'Content-Type': 'application/json'}
        cookies = { 
            'aws_session_token' : '',
            'aws_accesskey_id' : '',
            'aws_accesskey' : '',
            'email_password' : '',
            'email_address' : '',
            'file' : ""
        }

        response = None
        response = self.client.post('/upload', data=json.dumps(cookies), headers=headersFile)
        print("ho fatto richiesta)")
        time.sleep(10)
        
        if(response.status_code != 200):
            print("Error in upload")

        


        

class MailUser(HttpUser):
    
     wait_time = between(23, 38) 
     @task(2)
     def userTest(self):
        
        headersFile = {'Content-Type': 'application/json'}

        datajson = {
            'aws_session_token' : '',
            'aws_accesskey_id' : '',
            'aws_accesskey' : '',
            'email_password' : '',
            'email_address' : 'sdccdmdt@gmail.com',
            'nome': 'Test'
        }
        
        response = self.client.post('/sendemail', data=json.dumps(datajson), headers=headersFile)
        time.sleep(20)
        if(response.status_code != 200):
            print("Error in sendemail")
        

        
