from flask import Flask, escape, request
from flask_sqlalchemy import SQLAlchemy
import re
import os
import itertools
import datetime
import time

from environs import Env
from property_model import Property

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

app = Flask(__name__)
db = SQLAlchemy(app)

env = Env()
env.read_env()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')

council_names = [
    "https://planning.thanet.gov.uk",
    "https://pa.midkent.gov.uk"
]

for council_name in council_names:
    starting_date = datetime.datetime.now() - datetime.timedelta(days=3*365)

    while starting_date != datetime.datetime.now():
        driver = webdriver.Firefox()
        driver.get(
            council_name + "/online-applications/search.do?action=advanced")

        applicationReceivedStart = driver.find_element_by_id(
            "applicationReceivedStart")

        applicationReceivedEnd = driver.find_element_by_id(
            "applicationReceivedEnd")

        formatted_date = starting_date.strftime("%d/%m/%Y")

        applicationReceivedStart.send_keys(formatted_date)
        applicationReceivedEnd.send_keys(formatted_date)

        search_button = driver.find_element_by_css_selector(
            'input.button.primary')
        search_button.click()

        # To allow slow internet to catch up and not miss data and error
        time.sleep(4)

        page_of_results = BeautifulSoup(driver.page_source, "html.parser")

        address = page_of_results.find('ul', id='searchresults').find_all(
            'p', attrs={'class': 'address'})

        metainfo = page_of_results.find('ul', id='searchresults').find_all(
            'p', attrs={'class': 'metaInfo'})

        description_and_link = page_of_results.find(
            'ul', id='searchresults').find_all('a')

        cleaned_metainfo = []
        for x in metainfo:
            clean = re.sub(r'\>(.*?)\<', ' ', str(x))
            cleaner = clean.replace('\n', '')
            cleaned_metainfo.append(cleaner)

        cleaned_address = []
        for x in address:
            clean = re.sub(r'\>(.*?)\<', ' ', str(x))
            remove_class = clean.replace(r'<p class="address">', "")
            remove_tags = remove_class.replace(r'</p>', "")
            strip_spaces = remove_tags.strip()
            cleaned_address.append(strip_spaces)

        descriptions = []
        for x in description_and_link:
            clean = re.sub(r'<a href=(.*)">', ' ', str(x))
            remove_link = clean.replace(r'</a>', "")
            strip_spaces = remove_link.strip()
            descriptions.append(strip_spaces)

        urls = []
        for x in description_and_link:
            clean = re.search(r'(?=<a href=").*(?=">)', str(x)).group(0)
            remove_class = clean.replace(r'<a href="', "")
            remove_amp = remove_class.replace(r'amp;', "")
            append_council_name = council_name + remove_amp
            urls.append(append_council_name)

        refernce_numbers = []
        for x in cleaned_metainfo:
            clean = re.search(r'(?=Ref. No:).*(?=Received)', str(x)).group(0)
            remove_class = clean.replace(r'<span class="divider" /span> ', "")
            remove_ref_string = remove_class.replace(r'Ref. No:', "")
            strip_spaces = remove_ref_string.strip()
            refernce_numbers.append(strip_spaces)

        received_dates = []
        for x in cleaned_metainfo:
            clean = re.search(
                r'(?=Received:).*(?=Validated:)', str(x)).group(0)
            remove_class = clean.replace(r'<span class="divider" /span> ', "")
            remove_received_string = remove_class.replace(r'Received:', "")
            strip_spaces = remove_received_string.strip()
            received_dates.append(strip_spaces)

        validated_dates = []
        for x in cleaned_metainfo:
            clean = re.search(r'(?=Validated:).*(?=Status:)', str(x)).group(0)
            remove_class = clean.replace(r'<span class="divider" /span> ', "")
            remove_validated_string = remove_class.replace(r'Validated:', "")
            strip_spaces = remove_validated_string.strip()
            validated_dates.append(strip_spaces)

        statuses = []
        for x in cleaned_metainfo:
            clean = re.search(r'(?=Status:).*(?=)', str(x)).group(0)
            remove_tags = clean.replace(r'</p>', "")
            remove_status_string = remove_tags.replace(r'Status:', "")
            strip_spaces = remove_status_string.strip()
            statuses.append(strip_spaces)

        for (url, address, description, refernce_number, received_date, validated_date, status) in itertools.izip_longest(urls, cleaned_address, descriptions, refernce_numbers, received_dates, validated_dates, statuses):
            prop = Property(url=url, council_name=council_name, address=address, description=description, refernce_number=refernce_number,
                            received_date=received_date, validated_date=validated_date, status=status)
            db.session.add(prop)
            db.session.commit()

        print(starting_date, 'COMPLETED!')
        starting_date = starting_date + datetime.timedelta(+1)

        driver.close()
