from app import logger
from app.convertkit.ck_ui import ConvertKitUi
from app.less_annoying_crm.lac import Lac
from app.acuity import util


class Acuity:
    def __init__(self):
        self.new_acuity_user = False

    def process_any_new_acuity_users(self):
        logger.info("""
        *******************************
        Syncing
            Acuity --> Convert
            Acuity --> Less Annoying CRM
        *******************************
        """)


        util.login_to_acuity()
        util.export_acuity_users_to_csv()
        added_data, removed_data = util.compare_prev_and_curr_acuity_users()

        ###################
        # get email lists #
        ###################
        added_emails = []
        removed_emails = []

        for added in added_data:
            added_emails.append(added["email"])
        for removed in removed_data:
            removed_emails.append(removed["email"])

        ###########
        # compare #
        ###########
        subs_info = []
        for added_email in added_emails:
            if added_email not in removed_emails:
                ####################
                # process new user #
                ####################
                self.new_acuity_user = True
                logger.info(f"** new Acuity user with email '{added_email}'. Processing ... **")

                # find user info #
                for added in added_data:
                    if added["email"] == added_email:
                        subs_info.append(
                            {
                                "first_name": added["first_name"],
                                "last_name": added["last_name"],
                                "email": added["email"],
                                "note": "User initially added in Acuity"
                            }
                        )

        if self.new_acuity_user:
            logger.info(f"Adding {len(subs_info)} new Acuity user(s) to CK ...")
            ck_ui = ConvertKitUi()
            ck_ui.add_users_to_ck(users_info=subs_info)

            less_annoying_crm = Lac()
            less_annoying_crm.create_new_lac_user(users_info=subs_info)

        else:
            logger.info("No new Acuity users")

        util.archive_current_acuity_csv()

        logger.info("Done syncing any new Acuity users\n")



