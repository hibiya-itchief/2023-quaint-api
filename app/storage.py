import boto3
import imghdr
from PIL import Image
from io import BytesIO
from app.config import settings
import ulid
from fastapi import HTTPException

COMPRESS_QUALITY=50
try:
    s3 = boto3.client(
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
        s3.put_object(Bucket='quaint',Key='images/'+filename,Body=im_io.getvalue())
    except:
        raise HTTPException(500,"Internal Server Error")
    fileurl = "https://objectstorage.ap-tokyo-1.oraclecloud.com/n/nryxxlkqcfe6/b/quaint/o/images/"+filename
    return fileurl