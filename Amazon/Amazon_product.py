from bs4 import BeautifulSoup
import os
from selenium import webdriver
import re


# Open Chrome and paste url to load web page
# Speed: slow
# Compatibility: good, working as normal user
def get_html_source_by_selenium(url):
    driver_chrome = webdriver.Chrome("chromedriver.exe")# anh chị điền cái path dẫn vô file chromedriver.exe
    driver_chrome.get(url)
    return driver_chrome.page_source



# Define the catalog for getting the target products
base_url = 'https://www.amazon.com/s?k=smartphone&i=electronics&rh=n%3A2811119011&page=1&qid=1592874200&ref=sr_pg_0'
max_result = 1000000
filename = "product.csv" # anh chị điền cái path dẫn vô file product.csv

if __name__ == "__main__":
    # Showing flag for starting collecting product
    print('Collecting product list from Amazon from base_url = "{}" and saving to csv file'.format(base_url)) # khi có chuỗi {} và method format thì python sẽ tự động truyền param trong format vào {}

    total_product = 0
    url = base_url
    while True:
        print('Getting product list from: {}'.format(url))
        page = get_html_source_by_selenium(url) # lấy html source của trang web mà ta đang muốn lấy dữ liệu
        soup = BeautifulSoup(page, 'html.parser') # lấy tất cả dữ liệu của page

        # get searched products area
        product_areas = soup.find_all('div', {'class': 's-main-slot s-result-list s-search-results sg-row'}) # tìm khu vực chứa dữ liệu của tất cả sản phẩm 
        if len(product_areas) != 1: # một page chỉ có 1 khu vực sản phẩm 
            print('something went wrong, product area is not found')
            #  Will break if Amazon block
            break


        # get product_parts
        # do method find_all hay findChildren trả về 1 list nên khi dùng ta phải chỉ rõ nó là phần tử nào trong list 
        # thêm vào đó ở trên ta thấy product_areas có length = 1 nên nó chỉ có 1 index là 0
        product_parts = product_areas[0].findChildren('h2', {
            'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})

        # get products
        product_names = []
        product_ids = []
        for product_part in product_parts:
            product_link = product_part.a['href'].replace("%2F", "/") # get product url for next step
            matches = re.findall(r"\/dp\/.*\/", product_link, re.MULTILINE)  # after using re, we have '/dp/B079H6RLKQ/'
            product_ids.append(matches[0][4:-1])  # remove 4 first characters and 1 last character
            product_names.append(product_part.a.span.text[0: 20] + '...')
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

        #find next page
        last_buttons = soup.find_all('li', {'class': 'a-last'})
        #print(last_buttons)
        if len(last_buttons) != 1:
            break
        try:
            next_page_link = last_buttons[0].a.get('href')
            url = 'https://www.amazon.com' + next_page_link
        except:
            print('Next button is not found. Maybe this is the last page')
            break

    print('Finished product list')