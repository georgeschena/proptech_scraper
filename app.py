from flask import Flask, escape, request

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

app = Flask(__name__)


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
    applicationReceivedEnd.send_keys("02/03/2020")

    search_button = driver.find_element_by_css_selector('input.button.primary')
    search_button.click()

    page_of_results = BeautifulSoup(driver.page_source, "html.parser")

    address = page_of_results.find('ul', id='searchresults').find_all(
        'p', attrs={'class': 'address'})

    metainfo = page_of_results.find('ul', id='searchresults').find_all(
        'p', attrs={'class': 'metaInfo'})

    return 'bob'
