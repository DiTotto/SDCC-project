from locust import HttpUser, task, between, TaskSet
import json

class LoginUser(HttpUser):

    wait_time = between(23, 38) 

    @task(4)
    def login(self):

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {
                "aws_accesskey_id": "",
                "aws_accesskey": "",
                "aws_session_token": "",
                "email_address": "",
                "email_password": ""
            }

        response = self.client.post("/beta/login", 
                                    data=json.dumps(payload), headers=headers)

        

        if response.status_code == 200:
            print('Login DONE ')
        else:
            print('Login FAILED ')

class UploadUser(HttpUser):
        
    wait_time = between(23, 38)

    
    @task(2)
    def upload(self):

        data = { "key": "",
                "image": "" }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = self.client.post("/beta/upload", 
                                    data=json.dumps(data), headers=headers)

        print(response.text)

        if response.status_code == 200:
            print('Upload DONE ')
        else:
            print('Upload FAILED ')


class FaceRecognitionUser(HttpUser):

    wait_time = between(23, 38) 

    @task(2)
    def login(self):

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = ""

        response = self.client.post("/beta/facerec", 
                                    data=payload, headers=headers)

        print(response.text)

        if response.status_code == 200:
            print('FaceRec DONE ')
        else:
            print('FaceRec FAILED ')


class EmailUser(HttpUser):

    wait_time = between(23, 38) 

    @task(1)
    def email(self):

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {
            "key": "",
            "name": "Test",
            "url": "http://questoeuntest.com"
        }

        response = self.client.post("/beta/sendemail", 
                                    data=json.dumps(payload), headers=headers)


        if response.status_code == 200:
            print('Login DONE User1')
        else:
            print('Login FAILED User1')