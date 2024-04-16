import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


# Upload file to s3
def upload_file(file, object_name, bucket=settings.S3_BUCKET):

    # Construct public URL of image
    image_url = f'https://{bucket}.s3.amazonaws.com/{object_name}'

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_fileobj(
            file, bucket, object_name)

        # Set file can be accessed publicly
        s3_client.put_object_acl(
            Bucket=bucket,
            Key=object_name,
            ACL='public-read'
        )
    except ClientError as e:
        logging.error(e)
        return False
    return image_url
