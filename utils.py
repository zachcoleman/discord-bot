
import requests

async def url_request(url):
    resp = requests.get(url)
    return resp

