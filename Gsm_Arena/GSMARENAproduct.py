from bs4 import BeautifulSoup
import os
from selenium import webdriver
import re


# Open Chrome and paste url to load web page
# Speed: slow
# Compatibility: good, working as normal user
def get_html_source_by_selenium(url):
    driver_chrome = webdriver.Chrome("D:\\flask\\data\\chromedriver.exe")
    driver_chrome.get(url)
    return driver_chrome.page_source



# Define the catalog for getting the target products

brand_url = 'https://www.gsmarena.com/makers.php3' # url to all brand page
product_url ='https://www.gsmarena.com/{}'
max_result = 1000000
filename = ".\\data\\product2.csv"

# do trang này nó phân chia sản phẩm dựa theo brand, nên phải lấy link dẫn tới từng thương hiệu rồi sau đó mới cào được 
page = get_html_source_by_selenium(brand_url)
soup = BeautifulSoup(page, 'html.parser')
brand_area = soup.find_all('div', {'class': 'st-text'}) 
brand_names = brand_area[0].findChildren('td')

brand_links = []
for name in brand_names:
	link = name.a['href']
	brand_links.append(link)

#print(brand_links)
total_product = 0
for link in brand_links:
	url = product_url.format(link)
	print('Collecting product list from Amazon from base_url = "{}" and saving to csv file'.format(url))

	while True:
		print('Getting product list from: {}'.format(url))
		page = get_html_source_by_selenium(url)
		soup = BeautifulSoup(page, 'html.parser')

		product_areas = soup.find_all('div', {'class': 'makers'})
		if len(product_areas)!=1:
			print('something went wrong, product area is not found')
			break

		product_parts = product_areas[0].findChildren('li')

		product_names = []
		product_ids = []

		for product_part in product_parts:
		    product_link = product_part.a['href']
		    product_ids.append(product_link)
		    name = product_part.img['title']
		    product_names.append(name[0: 20] + '...')
		    total_product += 1
		    if total_product >= max_result:
		        break

		if len(product_ids) == 0:
		    break  # no more result

		result_str = ''
		for id, name in zip(product_ids, product_names):
			result_str += id + ',' + name.replace(',', '') + "\n"

		print(result_str)
		with open(filename, "a", encoding='utf-8') as f:
			f.write(result_str)
		print('Collected {}/{}'.format(total_product, max_result))

		if total_product >= max_result:
			break

		last_buttons = soup.find_all('a', {'class': 'pages-next'})
		if len(last_buttons) != 1:
			break
		try:
			next_page_link = last_buttons[0].a.get('href')
			url = product_url.format(next_page_link)
		except:
			print('Next button is not found. Maybe this is the last page')
			break
print("DONE")