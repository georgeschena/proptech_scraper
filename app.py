from flask import Flask, escape, request
from flask_sqlalchemy import SQLAlchemy
import re
import itertools

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://georgeschena:password@localhost/property_scraper'


class Properties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=True)
    refernce_number = db.Column(db.String(60),  nullable=True)
    received_date = db.Column(db.String(60),  nullable=True)
    validated_date = db.Column(db.String(60),  nullable=True)
    status = db.Column(db.String(60),  nullable=True)


@app.route('/')
def hello():
    driver = webdriver.Firefox()
    driver.get(
        "https://planning.thanet.gov.uk/online-applications/search.do?action=advanced")

    applicationReceivedStart = driver.find_element_by_id(
        "applicationReceivedStart")

    applicationReceivedEnd = driver.find_element_by_id(
        "applicationReceivedEnd")

    applicationReceivedStart.send_keys("01/03/2020")
    applicationReceivedEnd.send_keys("10/03/2020")

    search_button = driver.find_element_by_css_selector('input.button.primary')
    search_button.click()

    page_of_results = BeautifulSoup(driver.page_source, "html.parser")

    address = page_of_results.find('ul', id='searchresults').find_all(
        'p', attrs={'class': 'address'})

    metainfo = page_of_results.find('ul', id='searchresults').find_all(
        'p', attrs={'class': 'metaInfo'})

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

    refernce_numbers = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Ref. No:).*(?=Received)', str(x)).group(0)
        remove_class = clean.replace(r'<span class="divider" /span> ', "")
        remove_ref_string = remove_class.replace(r'Ref. No:', "")
        strip_spaces = remove_ref_string.strip()
        refernce_numbers.append(strip_spaces)

    received_dates = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Received:).*(?=Validated:)', str(x)).group(0)
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

    for a in statuses:
        prop = Properties(address=a)
        db.session.add(prop)
        db.session.commit()

    return str(statuses)
