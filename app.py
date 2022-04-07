from flask import Flask, request, redirect, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from utils import update_dynamoDB, upload_file_to_dropbox, send_to_s3
from dropbox_utils import get_token
from auth_settings import get_users
from logging_utils import get_logger_and_logFormatter, setup_log_file_handler, setup_log_stream_handler
import os

# Configure logging
LOG, formatter = get_logger_and_logFormatter()
setup_log_stream_handler(LOG, formatter)
log_file = './app_logs/webapp_logs.txt'
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))
setup_log_file_handler(log_file, LOG, formatter)
LOG.setLevel(20)
LOG.info("Logging info")
LOG.debug("Logging debug")
LOG.warning("Logging warning")

# Configure application
app = Flask(__name__)

app.config['VIDEO_UPLOADS'] = './uploads/'
if not os.path.exists(app.config['VIDEO_UPLOADS']):
    os.makedirs(app.config['VIDEO_UPLOADS'])

# Configure basic user authentication
auth = HTTPBasicAuth()
users = get_users()

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


# Web application    
@app.route('/', methods=['GET','POST'])
# @auth.login_required
def upload_file():
    """Main function for the application.
    Accepts a post request for a list of files and metadata as text
    Parses post request and sends files to s3 (parallelized uploads)
    """

    if request.method=="POST":
        
        # check if file in POST request
        if 'files[]' not in request.files:
            LOG.info('No file part')
            return redirect(request.url)
        
        # Write metadata to DynamoDB
        responses = update_dynamoDB(request)
        LOG.info(f"Metadata write with response {responses}")
        
        # Save videos locally to uploads folder
        for video in request.files.getlist('files[]'):
            video.save(os.path.join(app.config['VIDEO_UPLOADS'],video.filename))
            LOG.info(f"{video.filename} saved locally")
        
        uploads = os.listdir(app.config['VIDEO_UPLOADS'])
        local_files = [os.path.join(app.config['VIDEO_UPLOADS'],file) for file in uploads]
        
        # Send videos to s3
        for file in local_files:
            LOG.info(f"Attempting to send {file} to s3")
            response = send_to_s3(file)
            LOG.info(response)

        # Send videos to Dropbox
        for file in local_files:
            LOG.info(f"Uploading {file} to dropbox")
            dropbox_path = f"/Raw Uploads"
            upload_file_to_dropbox(dropbox_path, file)
            os.remove(file)
            LOG.info(f"{file} deleted from local server")
            
        
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=80)
