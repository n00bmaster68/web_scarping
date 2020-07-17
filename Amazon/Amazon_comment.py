from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import re
from selenium.webdriver.chrome.options import Options
import pandas
import time
import sys

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

def get_comments_from_page(driver, url):
    found_comments = []
    found_scores = []
    next_page_url = ''

    print('Getting comments from: {}'.format(url))
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get the comments area
    # dòng 45 -> 52 để check xem sản phẩm có còn tồn lại trên amazon hay không
    if soup.find_all('div', {'class': 'a-section a-spacing-top-large a-text-center no-reviews-section'}):
        return [], [], ''
    if soup.body is None:
        print("page body has nothing")
        return [], [], ''
    if soup.body.findAll(id='g'):  # is real page, not blocked but no comment
        print('This product is no longer existed')
        return [], [], ''
    # lấy khu vực chứa comment trong page
    # để tim xem class, id của nó là gì anh chị click chuột phải vào nó, rồi chọn inspect (kiểm tra nguồn)
    comment_areas = soup.find_all('div', {'id': 'cm_cr-review_list'})
    if len(comment_areas) != 1:
        
        if len(soup.body.findAll(text='Customer reviews')) > 0: 
            print('This product has no comment')
            return [], [], ''
        else:
            print('something went wrong, cannot find review_part')
        return [], [], ''
    
    # get all comments in review_part
    comment_parts = comment_areas[0].findChildren('div', {'class': 'a-section celwidget'})
    for comment_part in comment_parts:
        # get comment
        comment_texts = comment_part.findChildren('span', {'class': 'a-size-base review-text review-text-content'})
        if len(comment_texts) != 1:
            print('something went wrong, comment_texts is null')
            return [], [], ''
        found_comments.append(comment_texts[0].span.text)

        # get score
        comment_scores = comment_part.findChildren('i', {'data-hook': 'review-star-rating'})
        if len(comment_scores) != 1:
            sys.exit(3)
            return
        found_scores.append(comment_scores[0].span.text[0:1])

        # find the next page url
        next_buttons = soup.find_all('li', {'class': 'a-last'})
        try:
            if len(next_buttons) == 1:
                url = 'https://www.amazon.com' + next_buttons[0].a.get('href')
                next_page_url = url
        except:
            print('Next button is not found. Maybe this is the last page')

    return found_comments, found_scores, next_page_url
    

def get_product_comments(driver, product_id):
    all_comments = []
    all_scores = []
    page_no = 1
    url = 'https://www.amazon.com/product-reviews/{}/reviewerType=all_reviews'.format(product_id)

    while True:
        comments, scores, next_page_url = get_comments_from_page(driver, url)
        if len(comments) == 0:
            break  # no comment more
            # store results

        all_comments.extend(comments)
        all_scores.extend(scores)

        # print some reviews for debug
        log = ''
        for i in range(len(comments)): # comment_9845900003
            log = log + ('({}) "{}..." \n'.format(scores[i], comments[i][0:50]))
        print('Page {}: {} comments\n{}'.format(page_no, len(comments), log))

        if len(next_page_url) > 0:
            url = next_page_url
            page_no += 1
        else:
            break

        time.sleep(0.03)

    if all_comments is None and all_scores is None:
        return [], []
    return all_comments, all_scores

products_filename = '.\\data\\product.csv' #mấy anh chị đưa path của mình vào
comments_filename = '.\\data\\comments\\comment_{}.csv'#mấy anh chị đưa path của mình vào

if __name__ == "__main__":
    df = pandas.read_csv(products_filename, encoding='unicode_escape')
    driver = create_chrome_driver()

    for i in range(len(df)):
        product_id = df.iloc[i, 0]
        print('\n\n_____ Product {} {}/{} ___'.format(product_id, i, len(df)))
        real_comments_filename = comments_filename.format(product_id)

        print(real_comments_filename)
        print("=========")

        if (os.path.exists(real_comments_filename)):
            print('This product has been collected already, skip!')
        else:
            #write file
            comments, scores = get_product_comments(driver, product_id)
            content_str = ''
            for score, comment in zip(scores, comments):
                content_str += '{},{}\n'.format(score, comment.replace(',', ' '))
            with open(real_comments_filename, "w", encoding='utf-8') as f:
                f.write('score,comment\n' + content_str)

            # output for debug
            print('Collected {} comments'.format(len(comments)))

    driver.close()
    print('Done')