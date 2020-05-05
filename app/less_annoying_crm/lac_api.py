from app import logger
from app.config import Config
import requests
import json


class LacApi:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.api_base = f"https://api.lessannoyingcrm.com/?UserCode={Config.LAC_API_USER_CODE}&APIToken={Config.LAC_API_TOKEN}"

    def add_user_to_group(self, user_id, group_name):
        logger.info(f"Adding LAC user with id *{user_id}* to *{group_name}* group ...")
        func = "AddContactToGroup"
        params = {
            "ContactId": user_id,
            "GroupName": group_name
        }
        json_params = json.dumps(params)
        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)
        if resp["Success"] is True:
            logger.info(f"Added user with id *{user_id}* to *{group_name}* group")
        else:
            logger.error("Problem adding LAC user to group")

    def add_note_to_user(self, lac_user_id, note):
        logger.info("Adding note to LAC user ...")

        note = note.replace("&", "And")  # &s mess up URL

        func = "CreateNote"
        params = {
            "ContactId": lac_user_id,
            "Note": note
        }
        json_params = json.dumps(params)
        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)

        if resp["Success"]:
            logger.info("Successfully added note to LAC user")
        else:
            logger.error("Problem adding note to user")

    def create_new_user(self, user_data):
        logger.info(f"Creating LAC user (has email *{user_data['email']}*) ...")
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
        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)
        if resp["Success"]:
            user_id = resp["ContactId"]
            return user_id
        else:
            logger.error(f"Failed to add user with this data to LAC:\n\t{user_data}")

    def get_request(self, url):
        response = requests.request("GET", url)
        if response.status_code != 200:
            error_msg = json.loads(response.content)
            logger.exception(f"Failed API request. Reason:\n\t{error_msg}")
        else:
            resp_json = json.loads(response.content)
            return resp_json

    def get_all_contacts(self):
        first_page_contacts = self._get_page1_contacts()

        if len(first_page_contacts) == 500:  # max for LAC page
            subsequent_pg_contacts = self._get_contacts_after_page1()
            all_contacts = first_page_contacts.extend(subsequent_pg_contacts)
            return all_contacts
        else:
            return first_page_contacts

    def _get_page1_contacts(self):
        pg1_contacts = []

        func = "SearchContacts"
        params = {"SearchTerms": "", "Sort": "LastName", "NumRows": 500}
        json_params = json.dumps(params)

        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)

        if resp["Success"]:
            pg1_contacts = self._get_formatted_data_for_contact(resp)
        else:
            logger.error(f"Failed getting all LAC users")
        return pg1_contacts

    def _get_contacts_after_page1(self):
        subsequent_pg_contacts = []
        page_num = 2
        pg_contacts = 500  # init for pg 2

        while len(pg_contacts) == 500:
            resp = self._get_contacts_by_page(page_num=page_num)
            if resp["Success"]:
                pg_contacts = self._get_formatted_data_for_contact(resp)
                subsequent_pg_contacts.append(pg_contacts)
                page_num += 1
            else:
                logger.error(f"Failed getting all LAC users")
        return subsequent_pg_contacts

    def _get_contacts_by_page(self, page_num):
        func = "SearchContacts"
        params = {"SearchTerms": "", "Sort": "LastName", "NumRows": 500,
                  "Page": page_num}
        json_params = json.dumps(params)

        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)
        return resp

    def _get_formatted_data_for_contact(self, resp):
        contact_data_in_resp = []
        no_email_contacts = []

        for contact in resp["Result"]:
            if contact["Email"]:  # only process LAC contacts w emails
                email = contact["Email"][0]["Text"]

                try:
                    first_name = contact["FirstName"]
                except KeyError:
                    first_name = "NoFirstNameInLAC"

                num_emails = len(contact["Email"])
                if num_emails > 1:
                    logger.warning(f"{first_name} has more than 1 email. Only using first")

                contact_info = {
                    "first_name": first_name,
                    "email": email
                }
                contact_data_in_resp.append(contact_info)
            else:
                no_email_contacts.append(contact)
        return contact_data_in_resp

    def user_exists(self, email):
        func = "SearchContacts"
        params = {"SearchTerms": email}
        json_params = json.dumps(params)

        url = f"{self.api_base}&Function={func}&Parameters={json_params}"
        resp = self.get_request(url=url)

        if resp["Success"]:
            if resp["Result"]:
                logger.info(f"{email} already exists in LAC")
                return True
            else:
                logger.info(f"{email} doesn't exist in LAC yet")
                return False
        else:
            logger.error(f"Failed to check if LAC user exists")
