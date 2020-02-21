# Built-in modules
import sqlite3
import os
import time
import requests
import re

# Third-party modules
from bs4 import BeautifulSoup

# Local modules
import view_it_scraper
import google_maps
import settings

logger = settings.get_logger(__name__)


def fetch_database():
    start_time = time.time()
    sites = view_it_scraper.get_sites()
    img_id = ['ctl00_ContentPlaceHolder1_ucImageExpandView1_imgExterior',
              'ctl00_ContentPlaceHolder1_ucVideoExandView1_imgExterior']
    phone_id = 'ctl00_ContentPlaceHolder1_lblContactInfo'
    conn = sqlite3.connect(os.path.join(os.getcwd(), f'database/{settings.DATABASE_FILE}'))
    conn.row_factory = lambda cursor, row: row[0]
    conn.text_factory = str
    c = conn.cursor()

    sql_create = '''CREATE TABLE IF NOT EXISTS {tn}(
              website text, link text, closest_subway text, distance_to_closest_subway real,
              walk_time_to_closest_subway real, commute_time_to_destination real, address text, image_url text,
              image_name text, listing_price real, phone text, title text, posted_to_slack text
              )'''.format(tn=settings.DATABASE_NAME)
    c.execute(sql_create)

    for i in range(100):
        try:
            with conn:
                sql_select = '''SELECT link FROM {tn}'''.format(tn=settings.DATABASE_NAME)
                c.execute(sql_select)
                already_db = c.fetchall()
                cleaned_sites = [j for j in sites if j not in already_db]

                logger.info('#################################################################################')
                logger.info(f'Cleaned sites are: {len(cleaned_sites)}, already in db are: {len(already_db)}')
                logger.info('#################################################################################')

                for k in range(100):
                    location = google_maps.get_address(cleaned_sites[k])
                    if location[2] <= settings.MAX_WALK_TIME:
                        with requests.session() as r:
                            soup = BeautifulSoup(r.get(cleaned_sites[k]).content, 'lxml')
                            try:
                                img_url = soup.find('img', id=img_id[0]).attrs['src']
                            except AttributeError:
                                logger.info('Image ID was not found, trying Video ID instead for image.')
                                img_url = soup.find('img', id=img_id[1]).attrs['src']
                            img_name = soup.find('table', class_='tableDetail').text.replace('\n', '')
                            price = soup.find('span', id='ctl00_ContentPlaceHolder1_lblPrice').text
                            title = f'{img_name} | {location[4]} | ${price}'
                            phone = re.sub('[^0-9]', '', soup.find('span', id=phone_id).text.replace(u'\xa0', '')
                                           .split('(', 1)[-1])
                            if phone:
                                phone = f'{phone[:3]}-{phone[3:6]}-{phone[6:10]}'
                            else:
                                phone = 'N/A'
                            sql_insert = ''' INSERT INTO {a}(website, link, closest_subway, distance_to_closest_subway,
                            walk_time_to_closest_subway, commute_time_to_destination, address, image_url, image_name, 
                            listing_price, phone, title, posted_to_slack) VALUES ("{b}", "{c}", "{d}", {e}, {f}, {g}, 
                            "{h}", "{i}" , "{j}", {k}, "{l}", "{m}", "{n}")''' \
                                .format(a=settings.DATABASE_NAME, b='View It', c=cleaned_sites[k], d=location[0],
                                        e=location[1], f=location[2], g=location[3], h=location[4], i=img_url,
                                        j=img_name, k=price, l=phone, m=title, n=False)
                            c.execute(sql_insert)
                    else:
                        cleaned_sites.remove(cleaned_sites[k])

                    logger.info(f'#################################################################################')
                    logger.info(f'------ {(k + i * 10) * 100 / (len(cleaned_sites) + i * 10):.2f}% Completed ------')
                    logger.info(f'#################################################################################')
        except TypeError:
            conn.close()
            logger.info('#################################################################################')
            logger.info('SQlite File tried to use rate limited Google map result. Going to retry in 100 seconds.')
            logger.info('#################################################################################')
            time.sleep(100)

        except IndexError:
            conn.close()
            logger.info('Wrong index, end of cleaned list.')
            logger.info('#################################################################################')
            logger.info(f'------------- Updating DB took: {(time.time() - start_time):.2f} seconds -------------')
            logger.info('#################################################################################')
            return
        except sqlite3.OperationalError:
            conn.close()
            logger.info('#################################################################################')
            logger.info('ERROR with syntax skipping this link.')
            logger.info(sql_insert)
            logger.info('#################################################################################')
            continue

    logger.info('#################################################################################')
    logger.info(f'--- Updating DB took: {(time.time() - start_time):.2f} seconds ---')
    logger.info('#################################################################################')

    return


if __name__ == '__main__':
    # fetch_database(['https://classic.viewit.ca/vwExpandView.aspx?ViT=3156'])
    fetch_database()
