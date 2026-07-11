import urllib.request
import os
import time
import socket

url = "https://files.pythonhosted.org/packages/f1/32/05a56ab12d5601b5399e64b8f875362fb59c99218a5e74a99364a58516be/tensorflow_intel-2.16.1-cp310-cp310-win_amd64.whl"
filename = "tensorflow_intel-2.16.1-cp310-cp310-win_amd64.whl"
socket.setdefaulttimeout(15)

def download_with_resume(url, filename):
    if os.path.exists(filename):
        downloaded = os.path.getsize(filename)
    else:
        downloaded = 0
    
    headers = {}
    if downloaded > 0:
        headers['Range'] = f'bytes={downloaded}-'
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            content_length = response.headers.get('content-length')
            if content_length is None:
                # the server didn't return content-length, or doesn't support range
                total_size = 376000000 # approximate
            else:
                total_size = int(content_length) + downloaded
            
            print(f"Total size: {total_size}, Downloaded: {downloaded}")
            if downloaded >= 370000000 and content_length is None:
                 pass
            elif content_length and downloaded >= total_size:
                print("Already downloaded.")
                return True
                
            with open(filename, 'ab') as f:
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (1024*1024*10) < 65536: # print roughly every 10MB
                        print(f"Downloaded {downloaded/(1024*1024):.1f} MB")
            print(f"\nDownload complete! {downloaded} bytes")
            return True
    except Exception as e:
        print(f"\nError: {e}")
        return False

while True:
    if download_with_resume(url, filename):
        break
    print("Retrying in 2 seconds...")
    time.sleep(2)
