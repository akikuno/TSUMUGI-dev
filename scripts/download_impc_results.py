from urllib import request
from bs4 import BeautifulSoup
from http.client import RemoteDisconnected
from pathlib import Path

url = "http://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/release-17.0/results/"

response = request.urlopen(url)
soup = BeautifulSoup(response)
response.close()

save_directory = "data/impc/results"
Path(save_directory).mkdir(parents=True, exist_ok=True)

for x in soup.find_all("a"):
    content = x.text
    if r"." not in content:
        continue
    print(content)
    download_url = url + "/" + content
    save_name = save_directory + "/" + content
    if Path(save_name).exists():
        continue
    try:
        data = request.urlopen(download_url).read()
    except RemoteDisconnected:
        data = request.urlopen(download_url).read()
    with open(save_name, mode="wb") as f:
        f.write(data)

