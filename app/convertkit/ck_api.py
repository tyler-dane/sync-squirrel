from app.api import Api
from app import logger
from app.config import Config


class ConvertKitApi(Api):
    def __init__(self):
        super().__init__(uri_base="https://api.convertkit.com/v3", timeout=10)
        self.secret = Config.CONVERT_API_SECRET
        self.end = f"api_secret={self.secret}"

    def get_current_convertkit_users(self):
        logger.info("Getting current ConvertKit users ...")

        url = f"{self.base}/subscribers?api_secret={self.secret}"
        page_1_resp = self.get_request(url=url)

        curr_users = page_1_resp["subscribers"]

        if page_1_resp["total_pages"] > 1:
            curr_page = int(page_1_resp["page"])
            next_page = curr_page + 1
            total_pages = page_1_resp["total_pages"]

            while curr_page < total_pages:
                next_page_url = f"{url}&page={next_page}"
                next_page_resp = self.get_request(next_page_url)

                curr_users.extend(next_page_resp["subscribers"])

                curr_page += 1
                next_page += 1

        return curr_users

    def user_exists(self, user_email):
        curr_users = self.get_current_convertkit_users()

        for user in curr_users:
            if user["email_address"] == user_email:
                logger.info(f"{user_email} already exists in ConvertKit")
                return True

        logger.info(f"{user_email} does not already exist in ConvertKit")
        return False
