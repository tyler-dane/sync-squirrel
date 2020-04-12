from app.acuity.acuity import *
from app.convertkit.convertkit import ConvertKit
from app.less_annoying_crm.lac import Lac
from app import driver


def run():
    logger.info("Syncing all the things ...")

    ################
    # check acuity #
    ################
    acuity = Acuity()
    acuity.process_any_new_acuity_users()

    ####################
    # check convertkit #
    ####################
    ck = ConvertKit()
    ck.add_any_new_users_to_lac()

    ###########################
    # check less annoying crm #
    ###########################
    less = Lac()
    new_user_info = [
        {"first_name": "spam",
         "last_name": "AAAEggs",
         "email": "spamandeggs@fake.com"
         },
        {"first_name": "potato",
         "last_name": "AAAPotatoMan",
         "email": "potato@fake.com"
         }
    ]
    less.process_new_lac_users(users_info=new_user_info)  # TODO fix this

    less.add_any_new_users_to_convertkit()


if __name__ == "__main__":
    run()
    driver.quit()
