from app.convertkit.ck_api import ConvertKitApi
from app import logger


class CkMetadata:
    def __init__(self):
        self.ck_api = ConvertKitApi()

        self.all_forms = self._get_all_forms()
        self.form_subscribers = self._get_form_subscribers()

        self.all_sequences = self._get_all_sequences()
        self.sequence_subscribers = self._get_sequence_subscribers()

    def _get_all_forms(self):
        logger.info("Getting all CK form metadata ...")
        forms_url = f"{self.ck_api.base}/forms?{self.ck_api.end}"
        forms_resp = self.ck_api.get_request(forms_url)

        all_forms = forms_resp["forms"]
        return all_forms

    def _get_all_sequences(self):
        logger.info("Getting all CK sequences ...")
        seqs_url = f"{self.ck_api.base}/courses?{self.ck_api.end}"
        seqs_resp = self.ck_api.get_request(seqs_url)
        all_seqs = seqs_resp["courses"]

        return all_seqs

    def _get_form_subscribers(self):
        """
        [
            {
                "form_id": 123,
                "form_name": "2020 Goals",
                "subscriber_emails":
                    [
                        "java@yahoo.com",
                        "peter@parker.co"
                    ]
            },
            {
                "form_id": 345,
                "subscriber_emails":
                "form_name": "Fire Blanket Meditation",
                    []
            }
        ]
        """
        logger.info("Getting form subscribers ...")
        all_form_subs = []

        for form in self.all_forms:
            form_subs_url = f"{self.ck_api.base}/forms/{form['id']}/subscriptions/?{self.ck_api.end}"
            form_subs_resp = self.ck_api.get_request(form_subs_url)

            sub_emails = []
            for sub in form_subs_resp["subscriptions"]:
                sub_emails.append(sub["subscriber"]["email_address"])

            form_subs = {
                "form_id": form["id"],
                "form_name": form["name"],
                "subscriber_emails": sub_emails
            }

            all_form_subs.append(form_subs)

        return all_form_subs

    def _get_sequence_subscribers(self):
        """
        [
            {
                ""
            },
            {
            }
        ]
        """
        logger.info("Getting sequence subscribers ...")
        all_seq_subs = []

        for seq in self.all_sequences:
            seq_id = seq["id"]
            seq_name = seq["name"]
            seq_subs_url = f"{self.ck_api.base}/sequences/{seq_id}/subscriptions?{self.ck_api.end}"
            seq_subs_resp = self.ck_api.get_request(seq_subs_url)

            if seq_subs_resp["subscriptions"]:
                subs_emails = []

                for sub in seq_subs_resp["subscriptions"]:
                    sub_email = sub["subscriber"]["email_address"]
                    subs_emails.append(sub_email)

                seq_subs = {
                    "sequence_id": seq_id,
                    "sequence_name": seq_name,
                    "sequence_subscriber_emails": subs_emails
                }
                all_seq_subs.append(seq_subs)

        return all_seq_subs

    def get_user_metadata_note(self, ck_id, ck_email):
        logger.info("Getting metadata note for user ...")
        tags = self._get_tags_note(ck_id)
        subscribed_forms = self._get_forms_note(user_email=ck_email)
        sequences = self._get_sequences_note(user_email=ck_email)

        note = f"FORMS: {subscribed_forms} | TAGS: {tags} | SEQUENCES: {sequences}"

        return note

    def _get_tags_note(self, ck_id):
        logger.info(f"Getting tags for CK user {ck_id} ...")
        users_tags = []
        tags_url = f"{self.ck_api.base}/subscribers/{ck_id}/tags?{self.ck_api.end}"
        tags_resp = self.ck_api.get_request(tags_url)

        if tags_resp["tags"]:
            for t in tags_resp["tags"]:
                users_tags.append(t["name"])
            tags_note = ", ".join(users_tags)
            return tags_note
        else:
            return "No tags"

    def _get_forms_note(self, user_email):
        logger.info("Getting user's forms ...")
        users_forms = []
        for form in self.form_subscribers:
            if user_email in form["subscriber_emails"]:
                users_forms.append(form["form_name"])

        if users_forms:
            forms_note = ", ".join(users_forms)
            return forms_note
        else:
            return "No forms"

    def _get_sequences_note(self, user_email):
        logger.info("Getting user's sequences ...")
        users_sequences = []
        for seq in self.sequence_subscribers:
            if user_email in seq["sequence_subscriber_emails"]:
                users_sequences.append(seq["sequence_name"])

        if users_sequences:
            seqs_note = ", ".join(users_sequences)
            return seqs_note
        else:
            return "No sequences"
