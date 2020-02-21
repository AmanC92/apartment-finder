import logging
import os


# Logging parameters in a function that
# will be imported to every file
def get_logger(logger_name):
    log = logging.getLogger(logger_name)
    # Setting root logger to DEBUG
    log.setLevel(logging.DEBUG)
    # Formated logs to time:debug_level:module_name:message
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    # Logs are put to a subfolder logs in the current working directory
    log_dir = os.path.join(os.getcwd(), 'logs')
    log_fname = os.path.join(log_dir, 'main.log')
    file_handler = logging.FileHandler(log_fname)
    # Setting local logger of all scripts to Debug as well
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    return log


# What is the furthest walking distance in
# minutes you would like to be from the subway
MAX_WALK_TIME = 40

# What is the maximum price you are willing
# to pay for rent
PRICE = 1550

# Destination coordinates
# for commute time
COMMUTE_LAT_LON = ['43.774149', '-79.499784']

# Table name can be changed here
DATABASE_NAME = 'toronto_listings'
DATABASE_FILE = f'{DATABASE_NAME}.db'

# Slack Token API goes here
SLACKTOKEN = os.environ.get('slack_bot_token')

# Google Maps API Key goes here
GMAPYKEY = os.environ.get('gmap_key')

# Path for Google Chrome Driver goes here
GWEBDRIVER = os.environ.get('gwebdriver')
