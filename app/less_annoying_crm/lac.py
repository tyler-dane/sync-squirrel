import os
import time
import csv
import xlrd
from csv_diff import compare, load_csv
from xlrd.timemachine import xrange

from app import logger, util
from app.config import Config
from app.convertkit import ConvertKit
from app.less_annoying_crm.api import Api
from app.less_annoying_crm.lac_ui import LacUI


class Lac(Api):
    def __init__(self, timeout=15):
        super().__init__(timeout)
        self.lac_ui = LacUI()
        self.timeout = timeout
        self.api_base = f"https://api.lessannoyingcrm.com/?UserCode={Config.LAC_API_USER_CODE}&APIToken={Config.LAC_API_TOKEN}"

    # commented cuz API doesn't work
    """
    # def get_current_contacts(self):
    #     url = f"{self.api_base}&Function=SearchContacts&RecordType=Contacts"
    #     all_contacts = self.get_request(url)
    #
    #     # resp = self.get_request(url)
    #     return all_contacts
    """

    def get_any_new_contacts(self):
        ###################
        # export from LAC #
        ###################
        self.lac_ui.login()
        time.sleep(4)
        self.lac_ui.export_contacts()
        time.sleep(5)  # TODO more intelligent way to ensure file finished downloading
        xls_path = util.get_xls_path(search_dir=Config.DOWNLOADS_DIR)

        prev_contacts_csv = Config.LAC_PREV_PATH
        curr_contacts_csv = self._convert_xls_to_csv(xls_path)

        added, removed = self._get_added_and_removed_contacts(prev_csv=prev_contacts_csv, curr_csv=curr_contacts_csv)
        self.archive_downloaded_csv()

        ####################
        # get unique lists #
        ####################
        added_emails = []
        removed_emails = []

        for a in added:
            added_emails.append(a["email"])
        for r in removed:
            removed_emails.append(r["email"])

        ###########
        # compare #
        ###########
        new_user_data = []

        for added_em in added_emails:
            if added_em not in removed_emails:
                logger.info(f"** processing new user with email: {added_em}")

                # find user info and save #
                for a in added:
                    if a["email"] == added_em:
                        new_user_data.append({
                            "first_name": a["first_name"],
                            "email": a["email"]
                        })

        return new_user_data

    def _convert_xls_to_csv(self, xls_path):

        wb = xlrd.open_workbook(xls_path)
        sh = wb.sheet_by_index(0)  # all data in first (and only) sheet as of Mar 2020

        lac_csv = open(Config.LAC_CURR_PATH, 'w')
        wr = csv.writer(lac_csv, quoting=csv.QUOTE_ALL)

        for rownum in xrange(sh.nrows):
            wr.writerow(sh.row_values(rownum))

        lac_csv.close()
        return Config.LAC_CURR_PATH

    def _get_added_and_removed_contacts(self, prev_csv, curr_csv):
        compare_out = compare(
            load_csv(open(prev_csv)),
            load_csv(open(curr_csv))
        )

        added_data = []
        removed_data = []

        for added in compare_out["added"]:
            if added["First Name"] and added["Primary Email"]:
                added_data.append({"email": added["Primary Email"],
                                   "first_name": added["First Name"]})

        for removed in compare_out["removed"]:
            if removed["First Name"] and removed["Primary Email"]:
                removed_data.append({"email": removed["Primary Email"],
                                     "first_name": removed["First Name"]})

        return added_data, removed_data

    def add_any_new_users_to_convertkit(self):
        new_contacts = self.get_any_new_contacts()
        if new_contacts:
            logger.info("New LAC users found. Adding to convertkit...")
            self._add_new_users_to_convertkit(new_contacts_data=new_contacts)
        else:
            logger.info("No new LAC users since last time")

    def _add_new_users_to_convertkit(self, new_contacts_data):
        new_subs_info = []
        for new_lac_user in new_contacts_data:
            new_sub_data = {
                "first_name": new_lac_user["first_name"],
                "email": new_lac_user["email"]
            }
            new_subs_info.append(new_sub_data)

        ck = ConvertKit()
        ck.add_subscribers(new_subs_info)

    def archive_downloaded_csv(self):
        logger.info("Archiving (renaming) LAC users ...")
        os.rename(src=Config.LAC_CURR_PATH, dst=Config.LAC_PREV_PATH)


if __name__ == "__main__":
    less = Lac()
    less.add_any_new_users_to_convertkit()
