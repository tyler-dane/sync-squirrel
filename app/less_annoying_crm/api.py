class Api:
    def __init__(self, timeout=15):
        self.timeout = timeout

    """ commented out cuz api doesn't work
    def get_request(self, url):
        response = requests.request("GET", url)
        if response.status_code != 200:
            error_msg = json.loads(response.content)
            logger.exception(f"Failed API request. Reason:\n\t{error_msg}")
        else:
            resp_json = json.loads(response.content)
            return resp_json
    """
