from ftplib import FTP
import uuid

HOST = "public-ftp-e35e14a7-7465f0937c4a44be.elb.ap-northeast-1.amazonaws.com"
USER = "wei"
PASSWORD = "19901022Zw!"
FILENAME = "sample_data.zip"

def upload_ftp(filename):
    with FTP(host=HOST, user=USER, passwd=PASSWORD, encoding='utf-8') as ftp:
        ftp.login()
        with open(filename, "rb") as file:
            # Command for Uploading the file "STOR filename"
            ftp.storbinary(f"STOR {uuid.uuid4()}", file)

if __name__ == "__main__":
    upload_ftp(FILENAME)