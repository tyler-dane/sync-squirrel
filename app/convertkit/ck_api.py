from app.api import Api
from app.config import Config


class ConvertKitApi(Api):
    def __init__(self):
        super().__init__(uri_base="https://api.convertkit.com/v3", timeout=10)
        self.secret = Config.CONVERT_API_SECRET
        self.end = f"api_secret={self.secret}"
