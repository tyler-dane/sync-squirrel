from app import logger
from app.convertkit.ck_api import ConvertKitApi
from app.convertkit import util


class ConvertKit:
    def __init__(self):
        self.logged_in = False
        self.ck_api = ConvertKitApi()

    def add_any_new_users_to_lac(self):
        logger.info("""
        *******************************
        Syncing
            ConvertKit --> Less Annoying CRM
        *******************************
        """)

        # TODO fix so don't have to use local import and no circular top imports
        from app.less_annoying_crm.lac import Lac

        curr_users = self.ck_api.get_current_convertkit_users()

        if util.prev_users_file_exists():
            prev_users = util.get_previous_convertkit_users()

            if util.new_convertkit_user(curr_users, prev_users):
                logger.info("New ConvertKit users found. Adding them to Less Annoying CRM ...")
                new_users = util.get_new_users_data(curr_users=curr_users, prev_users=prev_users)

                less_annoying_crm = Lac()
                less_annoying_crm.create_new_lac_user(users_info=new_users)

            else:
                logger.info("No new ConvertKit users")
        else:
            logger.info(
                "No previous users file for ConvertKit. Recording current users into historical file for next time")
            util.save_users_to_prev_users_file(users=curr_users)

