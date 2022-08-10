from ftplib import FTP
import uuid

HOST = "172.31.71.15"
USER = "efs_wei"
PASSWORD = "19901022Zw!"
FILENAME = "sample_data.zip"

def upload_ftp(filename):
    with FTP(host=HOST, user=USER, passwd=PASSWORD) as ftp:
        ftp.set_debuglevel(2)
        ftp.login(user=USER, passwd=PASSWORD)
        with open(filename, "rb") as file:
            # Command for Uploading the file "STOR filename"
            ftp.storbinary(f"STOR {uuid.uuid4()}", file)

if __name__ == "__main__":
    upload_ftp(FILENAME)