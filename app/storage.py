import base64
import boto3
import imghdr
from PIL import Image
from io import BytesIO
from app.config import settings
import ulid
from fastapi import HTTPException

COMPRESS_QUALITY=50
try:
    s3_client = boto3.client(
    's3',
    region_name=settings.region_name,
    aws_secret_access_key=settings.aws_secret_access_key,
    aws_access_key_id=settings.aws_access_key_id,
    endpoint_url=settings.endpoint_url
    )
    s3_resource = boto3.resource(
    's3',
    region_name=settings.region_name,
    aws_secret_access_key=settings.aws_secret_access_key,
    aws_access_key_id=settings.aws_access_key_id,
    endpoint_url=settings.endpoint_url
    )
except:
    pass

def upload_to_oos(binary:bytes) ->str:
    try:
        image_type = imghdr.what(None,h=binary)
        if not(image_type=="png" or image_type=="jpeg"):
            raise HTTPException(415,"Invalid File Type:png or jpeg")
        
        im=Image.open(BytesIO(binary))
        if image_type=="png":
            im = im.convert('RGB')
        im_io=BytesIO()
        im.save(im_io, 'JPEG', quality = COMPRESS_QUALITY)
        
        filename=ulid.new().str+".jpg"
        s3_client.put_object(Bucket='quaint',Key='images/'+filename,Body=im_io.getvalue())
    except:
        raise HTTPException(500,"Internal Server Error")
    fileurl = "images/"+filename
    return fileurl

def upload_to_oos_public(binary:bytes) ->str:
    try:
        image_type = imghdr.what(None,h=binary)
        if not(image_type=="png" or image_type=="jpeg"):
            raise HTTPException(415,"Invalid File Type:png or jpeg")
        
        im=Image.open(BytesIO(binary))
        if image_type=="png":
            im = im.convert('RGB')
        im_io=BytesIO()
        im.save(im_io, 'JPEG', quality = COMPRESS_QUALITY)
        
        filename=ulid.new().str+".jpg"
        s3_client.put_object(Bucket='quaint-public',Key='images/'+filename,Body=im_io.getvalue())
    except:
        raise HTTPException(500,"Internal Server Error")
    fileurl = "https://objectstorage.ap-tokyo-1.oraclecloud.com/n/nryxxlkqcfe6/b/quaint-public/o/" + "images/"+filename
    return fileurl

def download_file_as_base64(key:str) ->str:
    try:
        response = s3_resource.Object("quaint", key).get()
        bytes_data=response['Body'].read()
        return base64.standard_b64encode(bytes_data)
    except:#keyがNone(=まだ画像を登録していない)ときはNoneを返す
        return None

def delete_image(image_url:str) ->None:
    try:
        s3_client.delete_object(Bucket='quaint', Key=image_url)
    except:
        raise HTTPException(500,"Internal Server Error")

def delete_image_public(image_url:str) ->None:
    try:
        file_key=image_url.split("/")[-1]
        s3_client.delete_object(Bucket='quaint-public', Key="images/"+file_key)
    except:
        raise HTTPException(500,"Internal Server Error")
