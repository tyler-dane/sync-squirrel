from app.acuity.acuity import *
from app.convertkit.convertkit import ConvertKit
from app.less_annoying_crm.lac import Lac
from app import driver


def run():
    logger.info("\nSyncing all the things ...")

    #####################################
    # sync new user in {SYSTEM1} to {system2}
    #####################################

    # ACUITY --> convertkit
    # ACUITY --> less annoying crm
    acuity = Acuity()
    acuity.process_any_new_acuity_users()

    # TODO start here
    # CONVERTKIT --> less annoying crm
    ck = ConvertKit()
    ck.add_any_new_users_to_lac()

    # LESS ANNOYING CRM --> convertkit
    less = Lac()
    less.add_any_new_users_to_convertkit()


if __name__ == "__main__":
    run()
    driver.quit()
