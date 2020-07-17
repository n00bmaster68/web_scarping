from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv

url = 'https://www.thegioididong.com/'
products = ['dtdd', 'laptop', 'may-tinh-bang']

def findProducts(soup):
    while True:
        button_next = soup.find_all('a', {'class': 'viewmore'})
        if len(button_next) != 1:
            break
        driver_chrome.find_element_by_xpath('/html/body/section/a').click() 
        time.sleep(1)
        soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')

def getIdName(product_parts, product, product_ids, product_names):
    for i in product_parts:
        product_link = i.a['href']
        matches = product_link[len(product) + 2:]
        product_ids.append(matches)
        product_names.append(i.a.h3.text)

def writeCSV(filename, product_ids, product_names):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for x, y in zip(product_ids, product_names):
            writer.writerow([x, y])

driver_chrome = webdriver.Chrome("chromedriver.exe")
filename = 'product.csv'
product_names = []
product_ids = []

for product in products:
    driver_chrome.get(url + product)
    soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')
    # find name product
    findProducts(soup)
    soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')
    product_areas = soup.find_all('ul', {'class': 'homeproduct'})
    product_parts = product_areas[0].findChildren('li', {'class': 'item'})
    # get link and name product
    getIdName(product_parts, product, product_ids, product_names)
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for x, y in zip(product_ids, product_names):
            writer.writerow([x, y])
    
driver_chrome.close()
