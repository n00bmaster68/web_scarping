from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import re
from selenium.webdriver.chrome.options import Options
import pandas
import time
import sys
""" trên gsm arena trong phần comment nó bao gồm cả câu hỏi và nó không cần thiết cho việc lấy ý kiến nên có 1 đoạn code để lọc ra phần đó 
"""
# This method creates an http connection to url directly without opening browser
# Speed: fast
# Compatibility: sometime this method is blocked by http server
def get_source_by_requests(url):
    page = requests.get(url)
    return page.text

# Open Chrome and paste url to load web page
# Speed: slow
# Compatibility: good, working as normal user
def create_chrome_driver():
    options = Options()
    driver_chrome = webdriver.Chrome("chromedriver.exe")
    return driver_chrome

"""
Function 'get_comments_from_page'
Input:
    driver: browser driver
    url: url to comment page
Return:
    comments[], scores[], next_page_url
"""
# chỉ lấy comment do trang này chỉ có câu chứ không có điểm 
def get_comments_from_page(driver, url):
    found_comments = []
    #found_scores = []
    next_page_url = ''

    print('Getting comments from: {}'.format(url))
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    
    comment_areas = soup.find_all('div', {'id': 'user-comments'})
    
    # get all comments in review_part
    comment_parts = comment_areas[0].findChildren('div', {'class': 'user-thread'})
    real_comment_parts = []
    #dòng 52 đến dòng 56 kiểm tra xem comment part là comment hay chỉ là câu hỏi, nếu là comment thì mới lấy
    for comment_part in comment_parts:
        if comment_part.findChildren('span', {'class':'uinreply-msg uinreply-msg-single'}) or comment_part.findChildren('span', {'class':'uinreply-msg'}):
            pass
        else:
            real_comment_parts.append(comment_part)
    #print(comment_parts)
    for comment_part in real_comment_parts:
        # get comment
        comment_texts = comment_part.findChildren('p', {'class': 'uopin'})
        #print(comment_texts)
        if comment_texts is None:
            print('something went wrong, comment_texts is null')
            return [], ''
        #print(comment_texts)

        found_comments.append(comment_texts[0].text)

        # find the next page url
        button_area = soup.find_all('div', {'class': 'sub-footer no-margin-bottom'})
        if button_area != []:
            #next_buttons = button_area[0].find_all('div', {'class': 'nav-pages'})
            next_buttons = button_area[0].find_all('a', {'title': 'Next page'})
            #print(next_buttons)
            if next_buttons is not None:
                s = str(next_buttons)
                s = s[9:-25]
                s = s.replace('"', '')
                #print (s)
                url = 'https://www.gsmarena.com/' + s
                next_page_url = url 
            else:
                print('Next button is not found. Maybe this is the last page')
                break 
        else:
            print('Next button is not found. This page has no button')
            break 
    return found_comments, next_page_url
    

def get_product_comments(driver, product_id):
    all_comments = []
    page_no = 1
    url = 'https://www.gsmarena.com/{}'.format(product_id)

    while True:
        comments, next_page_url = get_comments_from_page(driver, url)
        #print(comments)
        if len(comments) == 0:
            break  # no comment more
            # store results

        all_comments.extend(comments)

        # print some reviews for debug
        log = ''
        for i in range(len(comments)): # comment_9845900003
            log = log + ('"{}..." \n'.format(comments[i][0:50]))
        print('Page {}: {} comments\n{}'.format(page_no, len(comments), log))

        if next_page_url == 'https://www.gsmarena.com/' or next_page_url == '': 
            break
        else:
            #print(f'len(next_page_url): {len(next_page_url)}')
            url = next_page_url
            #print(f'next_page_url: {url}')
            page_no += 1
    if all_comments is None:
        return []
    return all_comments

# hàm preprocess_product_id dùng để tạo ra một cái product id đầy đủ cho web này do product id trên trang sản phẩm khác với product id trên trang review 
def preprocess_product_id (product_id):
    d = 0;
    length = len(product_id)-1
    while True :
        if product_id[length] == '-':
            break
        d = d + 1
        length = length -1
    return product_id[:len(product_id)-d]+'reviews-'+product_id[len(product_id)-d:]

products_filename = '.\\data\\product2.csv' #mấy anh chị đưa path của mình vào
comments_filename = '.\\data\\comments\\comment_{}.csv'#mấy anh chị đưa path của mình vào

if __name__ == "__main__":
    df = pandas.read_csv(products_filename, encoding='unicode_escape')
    driver = create_chrome_driver()

    for i in range(len(df)):
        product_id = df.iloc[i, 0]
        print('\n\n_____ Product {} {}/{} ___'.format(product_id, i, len(df)))
        real_comments_filename = comments_filename.format(product_id)

        real_product_id = preprocess_product_id(product_id)
        print(real_comments_filename)
        print("=========")

        if (os.path.exists(real_comments_filename)):
            print('This product has been collected already, skip!')
        else:
            #write file
            comments= get_product_comments(driver, real_product_id)
            content_str = ''
            for comment in comments:
                content_str += '{}\n'.format(comment.replace(',', ' '))
            with open(real_comments_filename, "w", encoding='utf-8') as f:
                f.write('comment\n' + content_str)

            # output for debug
            print('Collected {} comments'.format(len(comments)))

    driver.close()
    print('Done')
