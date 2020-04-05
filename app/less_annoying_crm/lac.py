import time
import csv
import xlrd

from app import logger
from app.config import Config
from app.convertkit import ConvertKit
from app.less_annoying_crm.api import Api
from app.less_annoying_crm.lac_ui import LacUI


class Lac(Api):
    def __init__(self, timeout=15):
        super().__init__(timeout)
        self.timeout = timeout
        self.current_users = self.get_current_contacts()
        self.previous_users = []
        # self.previous_users = self.get_historical_contacts()
        self.new_user_data = []
        # self.new_user_data = self.get_new_user_data()
        self.lac_ui = LacUI()

        self.api_base = f"https://api.lessannoyingcrm.com/?UserCode={Config.LAC_API_USER_CODE}&APIToken={Config.LAC_API_TOKEN}"

    def get_historical_contacts(self):
        with open(Config.LAC_HIST_USERS_FILE, "r+") as f:
            hist_contacts = f.read()
        return hist_contacts

    # def get_current_contacts(self):
    #     url = f"{self.api_base}&Function=SearchContacts&RecordType=Contacts"
    #     all_contacts = self.get_request(url)
    #
    #     # resp = self.get_request(url)
    #     return all_contacts

    def get_current_contacts(self):
        self.lac_ui.login()
        time.sleep(4)
        self.lac_ui.export_contacts()

        self._convert_xls_to_csv()
        return ""

    def _convert_xls_to_csv(self):
        wb = xlrd.open_workbook('your_workbook.xls')
        sh = wb.sheet_by_name('Sheet1')
        your_csv_file = open('your_csv_file.csv', 'wb')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

        for rownum in xrange(sh.nrows):
            wr.writerow(sh.row_values(rownum))

        your_csv_file.close()

    def get_new_user_data(self):
        new_users_data = []

        for curr_user in self.current_users:
            if curr_user not in self.previous_users:
                new_users_data.append({
                    "first_name": curr_user["FirstName"],
                    "email": curr_user["Email"]["Text"]
                })
        return new_users_data

    def add_any_new_users_to_convertkit(self):
        if self.new_user_data:
            logger.info("New LAC users found. Adding to convertkit...")
            self._add_new_users_to_convertkit()
        else:
            logger.info("No new LAC users since last time")

    def _add_new_users_to_convertkit(self):
        new_subs_info = []
        for new_lac_user in self.new_user_data:
            new_sub_data = {
                "first_name": new_lac_user["first_name"],
                "email": new_lac_user["email"]
            }
            new_subs_info.append(new_sub_data)

        ck = ConvertKit()
        ck.add_subscribers(new_subs_info)


if __name__ == "__main__":
    less = Lac()
    less.add_any_new_users_to_convertkit()
