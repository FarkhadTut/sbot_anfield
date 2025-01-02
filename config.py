import configparser


def telegram_token():
    config = configparser.ConfigParser()
    config.read('config.ini')
    TOKEN = config['TELEGRAM']['TOKEN']
    return TOKEN

## read SUPERUSERS
def get_superusers():
    with open("superusers.txt", "r") as superusers_file:
        SUPERUSERS = superusers_file.readlines()
    SUPERUSERS = [s.strip('\n') for s in SUPERUSERS] 
    return SUPERUSERS
