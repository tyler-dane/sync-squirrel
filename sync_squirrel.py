from app.acuity.acuity import *
from app.constants import Con
from app.convertkit.convertkit import ConvertKit
from app.less_annoying_crm.lac import Lac
from app import driver
from app import util


def run():
    logger.info(Con.START_SYNC_MSG)
    util.write_to_changelog("** Syncing all the things ... **")

    #####################################
    # sync new user in {SYSTEM1} to {system2}
    #####################################

    # ACUITY --> convertkit
    # ACUITY --> less annoying crm
    acuity = Acuity()
    acuity.process_any_new_acuity_users()

    # CONVERTKIT --> less annoying crm
    ck = ConvertKit()
    ck.add_any_new_users_to_lac()

    # LESS ANNOYING CRM --> convertkit
    less = Lac()
    less.add_any_new_users_to_convertkit()

    logger.info(Con.END_SYNC_MSG)
    util.write_to_changelog("Done syncing\n")


if __name__ == "__main__":
    run()
    driver.quit()
