import os, argparse, dropbox, time, requests

app_key = "7tr3276zwa55c08"
app_secret = "5qjuvoyyrck1ds4"
refresh_token = "riBTtNqltdkAAAAAAAAAARpL7WHrMwrh1IXNuPDhG7I2VWfXyXuEwbZ1n3VB32BH"
refresh_url = "https://api.dropbox.com/oauth2/token"

def get_token():
    params = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": app_key,
        "client_secret": app_secret
    }
    authorization = requests.post(refresh_url, data=params)
    access_token = authorization.json()['access_token']

    return access_token
    
class DropBoxUpload:
    def __init__(self,token,timeout=900,chunk=8):
        self.token = token
        self.timeout = timeout
        self.chunk = chunk

    def UpLoadFile(self,upload_path,file_path):
        dbx = dropbox.Dropbox(self.token,timeout=self.timeout)
        file_size = os.path.getsize(file_path)
        CHUNK_SIZE = self.chunk * 1024 * 1024
        dest_file_path = file_path.split('/')[-1]
        dest_path = upload_path + '/' + os.path.basename(dest_file_path)
        since = time.time()
        with open(file_path, 'rb') as f:
            uploaded_size = 0
            if file_size <= CHUNK_SIZE:
                dbx.files_upload(f.read(), dest_path)
                time_elapsed = time.time() - since
                print('Uploaded {:.2f}%'.format(100).ljust(15) + ' --- {:.0f}m {:.0f}s'.format(time_elapsed//60,time_elapsed%60).rjust(15))
            else:
                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=dest_path)
                while f.tell() <= file_size:
                    if ((file_size - f.tell()) <= CHUNK_SIZE):
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                        time_elapsed = time.time() - since
                        print('Uploaded {:.2f}%'.format(100).ljust(15) + ' --- {:.0f}m {:.0f}s'.format(time_elapsed//60,time_elapsed%60).rjust(15))
                        break
                    else:
                        dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE),cursor)
                        cursor.offset = f.tell()
                        uploaded_size += CHUNK_SIZE
                        uploaded_percent = 100*uploaded_size/file_size
                        time_elapsed = time.time() - since
                        print('Uploaded {:.2f}%'.format(uploaded_percent).ljust(15) + ' --- {:.0f}m {:.0f}s'.format(time_elapsed//60,time_elapsed%60).rjust(15), end='\r')
    
    def UploadURL(self, upload_path, url):
        since = time.time()
        dbx = dropbox.Dropbox(self.token, timeout=self.timeout)
        dbx.files_save_url(upload_path, url)
        time_elapsed = time.time() - since
        print(f'Upload completed in {time_elapsed}s')
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('upload_path', type=str, help='path in dropbox')
    parser.add_argument('file_path', type=str, help='path to file to upload')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--chunk', type=int, default=8, help='chunk size in MB')
    args = parser.parse_args()

    dbu = DropBoxUpload(get_token(), timeout=args.timeout, chunk=args.chunk)
    dbu.UpLoadFile(args.upload_path, args.file_path)

if __name__ == "__main__":
    main()
