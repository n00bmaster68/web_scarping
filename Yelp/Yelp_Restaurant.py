from bs4 import BeautifulSoup
import os
from selenium import webdriver
import re
import time


# Open Chrome and paste url to load web page
# Compatibility: good, working as normal user
def get_html_source_by_selenium(url):
    driver_chrome = webdriver.Chrome("chromedriver.exe")
    driver_chrome.get(url)
    return driver_chrome.page_source



base_url = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=San%20Francisco%2C%20CA&ns=1&start={}"
max_result = 1000000
filename = "product_yelp.csv"


if __name__ == "__main__":
    # Showing flag for starting collecting product
    print('Collecting product list from Amazon from base_url = "{}" and saving to csv file'.format(base_url))

    total_product = 0
    url = base_url
    # do bài này không hiên link của page tiếp theo, nên phải sử dụng vòng for để thay url để sang page tiếp theo
    for i in range (0, 162): 
        index = 30*i
        url = base_url.format(index)
        print('Getting product list from: {}'.format(url))
        page = get_html_source_by_selenium(url)
        soup = BeautifulSoup(page, 'html.parser')

        # get searched products area
        product_areas = soup.find_all('ul', {'class': 'lemon--ul__373c0__1_cxs undefined list__373c0__2G8oH'})
        if len(product_areas) == 0:
            print('something went wrong, product area is not found')
            break


        # get product_parts
        product_parts = product_areas[0].findChildren('h4',{'class':'lemon--h4__373c0__1yd__ heading--h4__373c0__27bDo alternate__373c0__2Mge5'})
        
        product_names = []
        product_ids = []
        for product_part in product_parts:
            product_link = product_part.a['href'] 
            product_ids.append(product_link)  
            product_names.append(product_part.span.a.text[0: 20] + '...')
            total_product += 1
            if total_product >= max_result:
                break


        if len(product_ids) == 0:
            break  # no more result

        #results => string
        result_str = ''
        for id, name in zip(product_ids, product_names):
            result_str += id + ',' + name.replace(',', '') + "\n"

        #write result to file
        print(result_str)
        with open(filename, "a", encoding='utf-8') as f:
            f.write(result_str)
        print('Collected {}/{}'.format(total_product, max_result))

        if total_product >= max_result:
            break

        time.sleep(0.6)
        
    print('Finished product list')
