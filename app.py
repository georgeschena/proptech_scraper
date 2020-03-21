from flask import Flask, escape, request
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

app = Flask(__name__)


class DatabaseObject:
    def __init__(self, address,
                 reference,
                 received_date,
                 validated_date,
                 status
                 ):
        self.address = address
        self.reference = reference
        self.received_date = received_date
        self.validated_date = validated_date
        self.status = status


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
        cleaner = clean.replace("\n", "")
        cleaned_address.append(cleaner)

    refernce_numbers = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Ref. No:).*(?=Received)', str(x)).group(0)
        refernce_numbers.append(clean)

    received_dates = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Received:).*(?=Validated:)', str(x)).group(0)
        received_dates.append(clean)

    validated_dates = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Validated:).*(?=Status:)', str(x)).group(0)
        validated_dates.append(clean)

    statuses = []
    for x in cleaned_metainfo:
        clean = re.search(r'(?=Status:).*(?=)', str(x)).group(0)
        statuses.append(clean)

    return str(cleaned_address)
