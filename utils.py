import requests
import boto3
from dropbox_utils import DropBoxUpload, get_token


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}
DYNAMODB_TABLE = 'prediction_results_and_metadata'


def fetch_presignedS3_post(filename):
    """Retrieves a presigned post url from the lambda function (bucket configured in lambda)"""
    response = requests.get(f"https://7kodaj0lib.execute-api.us-east-1.amazonaws.com/default/getPresignedURL?object={filename}")
    return response.json()

def allowed_file(filename):
    """Checks that the file uploads have an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_to_s3(local_path):
    """Gets presigned url and sends file to bucket"""
    
    if allowed_file(local_path):
        fname = local_path.split('/')[-1]
        
        # Get s3 upload permissions
        permissions = fetch_presignedS3_post(fname)
        # print({'S3 upload permissions': permissions})
        
        # Send file
        files = {'file': open(local_path, 'rb')}
        # print(f'Sending {local_path} to s3')
        upload_response = requests.post(permissions['url'], data=permissions['fields'], files=files)
    
        return upload_response
    
    else:
        return 'Invalid file type'


def update_dynamoDB(request):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE)
    responses = []
    
    for file in request.files.getlist('files[]'):
        filename = file.filename.replace(" ","_") # Because the s3 event that triggers the batch job does this... need naming consistency
        response = table.update_item(
            Key={'Long File Name':filename},
            UpdateExpression='SET camera_number = :cam, card_number = :card, lattitude = :lat, longitude = :long, submitter = :sub',
            ExpressionAttributeValues={
                ':cam': request.form['Camera Number'],
                ':card': request.form['Card Number'],
                ':lat': request.form['Lattitude'],
                ':long': request.form['Longitude'],
                ':sub': request.form['fullname']
            }
            )
        responses.append(response)
    return responses
    

def upload_file_to_dropbox(dropbox_path, local_path):
    token = get_token()
    default_timeout = 900
    default_chunk = 8

    dbu = DropBoxUpload(token, timeout=default_timeout, chunk=default_chunk)
    dbu.UpLoadFile(dropbox_path, local_path)
    
