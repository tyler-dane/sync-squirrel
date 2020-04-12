import json
import os
import time
import csv
import xlrd
from csv_diff import compare, load_csv
from xlrd.timemachine import xrange

from app import logger, util
from app.config import Config
from app.convertkit.convertkit import ConvertKit
from app.less_annoying_crm.lac_api import LacApi
from app.less_annoying_crm.lac_ui import LacUI


class Lac:
    def __init__(self, timeout=15):
        self.lac_ui = LacUI()
        self.lac_api = LacApi()
        self.timeout = timeout
        self.new_user_data = []  # to be added once needed

    def get_any_new_lac_users(self):
        ###################
        # export from LAC #
        ###################
        self.lac_ui.login()
        time.sleep(4)
        self.lac_ui.export_current_contacts()
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

        self.new_user_data = new_user_data
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

    def process_new_lac_users(self, users_info):
        """Called by other systems (Acuity, ConvertKit)"""
        logger.info("Adding new user(s) to LessAnnoying CRM ...")

        for lac_user in users_info:
            lac_user_id = self._create_new_lac_user(user_data=lac_user)
            self._add_lac_user_to_group(user_id=lac_user_id, group_name=Config.LAC_NEW_USER_GROUP_NAME)
            if lac_user["note"]:
                self._add_note_to_lac_user(lac_user_id=lac_user_id, note=lac_user["note"])
            else:
                logger.warning("No note provided for user")

        # TODO update prev_lac file (after converting to JSON
        logger.info("Done processing new LessAnnoying CRM user(s)")

    def _create_new_lac_user(self, user_data):
        func = "CreateContact"
        params = {
            "FirstName": user_data["first_name"],
            "LastName": user_data["last_name"],
            "Email": [
                {
                    "Text": user_data["email"], "Type": "Work"
                }
            ]
        }
        json_params = json.dumps(params)
        url = f"{self.lac_api.api_base}&Function={func}&Parameters={json_params}"
        resp = self.lac_api.get_request(url=url)
        if resp["Success"]:
            user_id = resp["ContactId"]
            return user_id
        else:
            logger.error(f"Failed to add user with this data to LAC:\n\t{user_data}")

    def _add_lac_user_to_group(self, user_id, group_name):
        logger.info(f"Adding user with id *{user_id}* to *{group_name}* group ...")
        func = "AddContactToGroup"
        params = {
            "ContactId": user_id,
            "GroupName": group_name
        }
        json_params = json.dumps(params)
        url = f"{self.lac_api.api_base}&Function={func}&Parameters={json_params}"
        resp = self.lac_api.get_request(url=url)
        if resp["Success"] is True:
            logger.info(f"Added user with id *{user_id}* to *{group_name}* group")
        else:
            logger.error("Problem adding LAC user to group")

    def _add_note_to_lac_user(self, lac_user_id, note):
        func = "CreateNote"
        params = {
            "ContactId": lac_user_id,
            "Note": note
        }
        json_params = json.dumps(params)
        url = f"{self.lac_api.api_base}&Function={func}&Parameters={json_params}"
        resp = self.lac_api.get_request(url=url)

        if resp["Success"]:
            logger.info("Successfully added note to LAC user")
        else:
            logger.error("Problem adding note to user")

    def add_any_new_users_to_convertkit(self):
        self.get_any_new_lac_users()
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
        ck.add_users_to_ck(new_subs_info)

    def archive_downloaded_csv(self):
        logger.info("Archiving (renaming) LAC users ...")
        os.rename(src=Config.LAC_CURR_PATH, dst=Config.LAC_PREV_PATH)

# if __name__ == "__main__":
#     less = Lac()
#
#     new_user_info = [
#         {"first_name": "spam",
#          "last_name": "AAAEggs",
#          "email": "spamandeggs@fake.com"
#          },
#         {"first_name": "potato",
#          "last_name": "AAAPotatoMan",
#          "email": "potato@fake.com"
#          }
#     ]
#
#     less.process_new_lac_users(users_info=new_user_info)
#     # less.add_any_new_users_to_convertkit()
