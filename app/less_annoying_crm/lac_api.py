from app import logger
from app.config import Config
import requests
import json


class LacApi:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.api_base = f"https://api.lessannoyingcrm.com/?UserCode={Config.LAC_API_USER_CODE}&APIToken={Config.LAC_API_TOKEN}"

    def get_request(self, url):
        response = requests.request("GET", url)
        if response.status_code != 200:
            error_msg = json.loads(response.content)
            logger.exception(f"Failed API request. Reason:\n\t{error_msg}")
        else:
            resp_json = json.loads(response.content)
            return resp_json


"""


payload = {}
headers = {
  'Cookie': 'Session_LACRM=1tm1h6dtha8h779250lrnotq51'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))


"""
