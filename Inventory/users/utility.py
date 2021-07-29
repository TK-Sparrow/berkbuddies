import json
import requests
import secrets
import os
import boto3
from inventory import client
from PIL import Image
from flask import current_app,url_for,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from inventory.config import Config
from botocore.config import Config as s3_config
from boto3.s3.transfer import TransferConfig

def getResetTokenKey(data_to_send,expires_sec=1800):
	s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
	return s.dumps({'user_data': data_to_send}).decode('utf-8')


def send_register_email(mailId):
    token = getResetTokenKey(mailId)
    body = url_for('users.continue_register', token=token, _external=True)
    sub = "Continue the Registeration"
    
    url = "https://f9k2ymvbza.execute-api.ap-south-1.amazonaws.com/deploy_v1/send-request-mail"
    #url = "https://w97r01av5k.execute-api.us-east-2.amazonaws.com/prod/sendmail"

    payload = json.dumps({  "sub":sub, "to": mailId,  "token": body})
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = payload)
def send_resent_email(mailId):
    token = getResetTokenKey(mailId)
    body = url_for('users.change_password', token=token, _external=True)
    sub = "Reset Your Password"

    url = "https://f9k2ymvbza.execute-api.ap-south-1.amazonaws.com/deploy_v1/send-request-mail"
    #url = "https://w97r01av5k.execute-api.us-east-2.amazonaws.com/prod/sendmail"

    payload = json.dumps({ "sub":sub, "to": mailId,  "token": body})
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

def verify_register_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        user_data = s.loads(token)['user_data']
    except:
        return None
    return user_data



def save_picture(form_picture,folder_name="product_posts"):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/'+folder_name, picture_fn)
    i = Image.open(form_picture)
    output_size = (750, 750)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def start_verification(to, channel='sms'):
    if channel not in ('sms', 'call'):
        channel = 'sms'

    service = current_app.config.get("VERIFICATION_SID")
    try:
        verification = client.verify \
            .services(service) \
            .verifications \
            .create(to=to, channel=channel)
        
        return verification.sid
    except Exception as e:
        return "error"


def check_verification(phone, code):
    service = current_app.config.get("VERIFICATION_SID")
    
    try:
        verification_check = client.verify \
            .services(service) \
            .verification_checks \
            .create(to=phone, code=code)

        if verification_check.status == "approved":
            return "approved"
        else:
            return "not approved"
    except Exception as e:
        return "error"

# def to_s3(image_file,folder_name="product_posts"):
#     bucket = Config.BUCKET
#     content_type ='image/jpeg'
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(image_file.filename)
#     picture_fn = random_hex + f_ext

#     config = s3_config(s3={"use_accelerate_endpoint": True})

#     client = boto3.resource('s3',
#             aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
#                              region_name="ap-south-1",
#                              config=config)
    
#     client.Bucket(bucket).put_object(Body=image_file.read(),
#                       Key=folder_name+'/'+picture_fn,ACL='public-read',
#                       ContentType=content_type)

#     return picture_fn

def delete_img_s3(image_name):
    bucket = Config.BUCKET
    client = boto3.resource('s3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
    
    client.Bucket(bucket).Object(image_name).delete()

    return "done"


def to_s3(image_file,folder_name="product_posts"):
    bucket = Config.BUCKET
    content_type ='image/jpeg'

    picture_fn=save_picture(image_file)
    picture_path = os.path.join(current_app.root_path, 'static/'+folder_name, picture_fn)

    # config = s3_config(s3={"use_accelerate_endpoint": True})

    client = boto3.client('s3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)

    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)

    client.upload_file(picture_path, bucket, folder_name+'/'+picture_fn,
    ExtraArgs={ 'ACL': 'public-read', 'ContentType': content_type},
    Config = config
    )
    #print(picture_fn)
    os.remove (picture_path)
    return picture_fn
