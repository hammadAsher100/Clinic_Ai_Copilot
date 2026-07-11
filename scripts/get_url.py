import urllib.request
import json

url = "https://pypi.org/pypi/tensorflow-intel/2.16.1/json"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    
for url_info in data['urls']:
    if 'cp310' in url_info['filename'] and 'win_amd64' in url_info['filename']:
        print(url_info['url'])
