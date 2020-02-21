# Built-in modules
import time
import re

# Third-party modules
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium import common
from bs4 import BeautifulSoup

# Local modules
import settings

logger = settings.get_logger(__name__)

start_time = time.time()

# Urls to be scraped, each url corresponds to a different
# 'region' search as labeled by ViewIt
urls = ['https://classic.viewit.ca/toronto.aspx?CID=353',
        'https://classic.viewit.ca/toronto.aspx?CID=49',
        'https://classic.viewit.ca/toronto.aspx?CID=354',
        'https://classic.viewit.ca/toronto.aspx?CID=355',
        'https://classic.viewit.ca/toronto.aspx?CID=14',
        'https://classic.viewit.ca/toronto.aspx?CID=356',
        'https://classic.viewit.ca/city/northyork.aspx?CID=360',
        'https://classic.viewit.ca/city/northyork.aspx?CID=359',
        'https://classic.viewit.ca/city/northyork.aspx?CID=361'
        ]

# Listing page table id's
view_dict = {
    1: ['ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl03_lnkIntersection',
        'ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl03_lblPrice'],
    2: ['ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl04_lnkIntersection',
        'ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl04_lblPrice'],
    3: ['ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl05_lnkIntersection',
        'ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl05_lblPrice'],
    4: ['ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl06_lnkIntersection',
        'ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl06_lblPrice'],
    5: ['ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl07_lnkIntersection',
        'ctl00_ContentPlaceHolder1_ucListingsGrid1_grdListings_ctl07_lblPrice'],
}

# Search page id's
total_page_id = 'ctl00_ContentPlaceHolder1_ucListingsGrid1_lblPageCount'
pr_900_199_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkPrice3'
pr_1200_1599_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkPrice4'
bachelor_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkBachelor'
bedroom_1_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkBedroom1'
basement_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkBasement'
furnished_all_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_chkFurnishedAll'
search_button_id = 'ctl00_ContentPlaceHolder1_ucSearchDetails1_btnSearch'


def view_page(pages, driver):
    sites = []
    for page in range(1, pages+1):
        html_pages = driver.page_source
        soup_pages = BeautifulSoup(html_pages, "lxml")
        for i in view_dict:
            try:
                listing = soup_pages.find(id=view_dict[i][0]).get('href')
                price = soup_pages.find(id=view_dict[i][1]).text
                price_clean = re.sub("[^0-9]", "", price)

                # This will take the maximum price you have set in the settings
                # and only add sites that are at or under that pirce
                if price_clean and int(price_clean) <= settings.PRICE:
                    sites += ['https://classic.viewit.ca/' + listing]
            except AttributeError:
                logger.exception('Could not find listing or price while scraping pages.')
                continue
        if page != pages:
            # This is checking to see if it is not the last page of the number of pages.
            # If it is not, then select the next page in the list.
            select_pages = Select(driver.find_element_by_id('ctl00_ContentPlaceHolder1_ucListingsGrid1_cboPages'))
            select_pages.select_by_value(str(page))
    return sites


def get_sites():
    all_urls = []

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    # Google Web Driver path is inputted here from settings
    with webdriver.Chrome(settings.GWEBDRIVER, options=options) as driver:
        for url in urls:
            driver.get(url)
            for j in range(0, 3):
                try:
                    if not driver.find_element_by_id(pr_900_199_id).is_selected():
                        driver.find_element_by_id(pr_900_199_id).click()
                    if not driver.find_element_by_id(pr_1200_1599_id).is_selected():
                        driver.find_element_by_id(pr_1200_1599_id).click()
                    if not driver.find_element_by_id(bachelor_id).is_selected():
                        driver.find_element_by_id(bachelor_id).click()
                    if not driver.find_element_by_id(bedroom_1_id).is_selected():
                        driver.find_element_by_id(bedroom_1_id).click()
                    if driver.find_element_by_id(basement_id).is_selected():
                        driver.find_element_by_id(basement_id).click()
                    if not driver.find_element_by_id(furnished_all_id).is_selected():
                        driver.find_element_by_id(furnished_all_id).click()
                    driver.find_element_by_id(search_button_id).click()
                    break
                except common.exceptions.NoSuchElementException:
                    time.sleep(0.5)
                    continue
                except common.exceptions.StaleElementReferenceException:
                    time.sleep(0.5)
                    continue

            for i in range(3):
                try:
                    num_pages = int(driver.find_element_by_id(total_page_id).text)
                    all_urls += view_page(num_pages, driver)
                    break
                except common.exceptions.NoSuchElementException:
                    time.sleep(1)
                    continue
    logger.info('###########################################################################')
    logger.debug(f'The number of non-duplicate urls are: {len(list(set(all_urls)))}.')
    logger.debug(f'---View It Scraper took {(time.time() - start_time):.2f}')
    logger.info('###########################################################################')

    return list(set(all_urls))
