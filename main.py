# Built-in modules
import sqlite3
import os
import time

# Third-party modules
import slack
from slack import errors as se

# Local modules
import settings
import sqlite_db

# Setting up logging
logger = settings.get_logger(__name__)

# Setting up Slack client using Slack API Token inputted in settings
client = slack.WebClient(token=settings.SLACKTOKEN)


# Main function that will post to Slack channel
# You can set the default slack channel here
def post_slack_all(chan='#toronto-apartments', emoji=':robot_face:'):
    # This function will post up to a 1000
    # messages to slack, if you need to post
    # more than this then increase the range here
    for j in range(100):
        try:
            # Change name of datbase in settings if desired
            # Setting up connection to database in database folder of
            # current working directory
            conn = sqlite3.connect(os.path.join(os.getcwd(), f'database/{settings.DATABASE_FILE}'))

            # Connection parameter settings changed so that
            # you get a string and list instead of bytes and a tuple
            # from sqlite table
            conn.row_factory = lambda cursor, row: list(row)
            conn.text_factory = str
            c = conn.cursor()

            # Selecting all rows in database that have not
            # already been posted to slack
            sql_select = '''SELECT * FROM {tn} WHERE posted_to_slack='False' '''.format(tn=settings.DATABASE_NAME)
            c.execute(sql_select)
            rows = c.fetchall()

            logger.info('#################################################################################')
            logger.info(f'------------------------- Rows fetched are: {len(rows)}------------------------- ')
            logger.info('#################################################################################')

            if rows:
                with conn:
                    # This is so that the connection will close and save
                    # every 10 iterations incase of Slack API rate limit
                    # exception
                    for i in range(10):
                        try:
                            url = rows[i][1]
                            client.chat_postMessage(channel=chan, blocks=build_block(rows[i]), icon_emoji=emoji)
                            sql_update = '''UPDATE {tn} SET posted_to_slack=1 WHERE link='{u}' '''\
                                         .format(tn=settings.DATABASE_NAME, u=url)
                            c.execute(sql_update)
                        except IndexError:
                            logger.info('All items sent to slack, end of list.')
                            return
            else:
                return
        except se.SlackApiError:
            # Waiting to no longer be rate limited by Slack API
            time.sleep(60)
            continue


# This function takes data that was collected earlier
# and stored in a table and converts it to a Slack
# formatted Block that can be sent with Slack's API
def build_block(table_data):
    # Adding block texts as variables here so if need be
    # in the future they can easily be updated here
    subway = table_data[2].replace('_', ' ').title()
    url, walk_time, commute_time = table_data[1], str(table_data[4]), str(table_data[5])
    address, img_url, img_name = table_data[6], table_data[7], table_data[8]
    price, phone, title = str(int(table_data[9])), table_data[10], table_data[11]

    block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": title
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Link"
                },
                "url": url
            }
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": img_name,
                "emoji": True
            },
            "image_url": img_url,
            "alt_text": "Example Image"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Listing Price: $" + price + '*'
                },
                {
                    "type": "mrkdwn",
                    "text": "*Address: " + address + '*'
                },
                {
                    "type": "mrkdwn",
                    "text": "Nearest Subway: " + '_' + subway + '_'
                },
                {
                    "type": "mrkdwn",
                    "text": "Walk time (" + subway + ") : " + '_' + walk_time + ' min' + '_'
                },
                {
                    "type": "mrkdwn",
                    "text": "Commute time: " + '_' + commute_time + ' min' + '_'
                },
                {
                    "type": "mrkdwn",
                    "text": "Contact: " + phone
                }
            ]
        },
        {
            "type": "divider"
        }
    ]
    return block


if __name__ == '__main__':
    # First call to update database
    sqlite_db.fetch_database()
    # Second call to post updated databse
    # to slack
    post_slack_all()
