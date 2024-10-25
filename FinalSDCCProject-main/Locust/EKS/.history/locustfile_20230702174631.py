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
        # while response is None:
        #     print("sleep")
        #     time.sleep(1)
        time.sleep(10)
        
        if(response.status_code != 200):
            print("Error in upload")

        


        

class MailUser(HttpUser):
    
     wait_time = between(23, 38) 
     @task(2)
     def userTest(self):
        
        headersFile = {'Content-Type': 'application/json'}

        datajson = {
            'aws_session_token' : 'FwoGZXIvYXdzEMb//////////wEaDKpZQbQE2/4oEAwrLCK+Aav0F8APC+ET721rAJ1RvByTzjHXXAwJNbtBAHvIzhv3KV6ybArZe/vH9HJFtx11uEce0cZsN4tnKGXgmv2OvBLNoaxGxOtusMjp434EgCfQpLPyqwSemQ9IAd4KwlPBFpRPTXXQqRbBhWG2BnzyzpSdA1hbKlw8jc5CKFAC1+R369YiaUZlhxRsxAs8+nPBChQjz1LDtPlsJOjKFgT3dTHP99Er6j217644AVkxa6XlQ395JyI+zlh/fibrFYkosLDdpAYyLaqfey6lkfVFKVpaOgwUB4qMWMRsBMpJwPvElo/aaRkUSXaJCZ/vOIQSdZL3jg==',
            'aws_accesskey_id' : 'ASIAQEZ3HMBUMVFB7JUX',
            'aws_accesskey' : '9AWjV995LFe1YCgON8qU6Qp8pI/fbIA+sjMex9JC',
            'email_password' : 'ecfvmlqnrfqtedfb',
            'email_address' : 'sdccdmdt@gmail.com',
            'nome': 'Test'
        }
        
        response = self.client.post('/sendemail', data=json.dumps(datajson), headers=headersFile)
        time.sleep(20)
        if(response.status_code != 200):
            print("Error in sendemail")
        

        
