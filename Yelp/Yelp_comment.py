from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import re
from selenium.webdriver.chrome.options import Options
import pandas
import time
import sys

#bước 1: tìm div (hoặc tag khác) chứa tất cả comments
#bước 2: từ div (hoặc tag khác) ở bước 1, tìm ra từng comment, điểm và tên người dùng tuỳ trường hợp

def get_source_by_requests(url):
    page = requests.get(url)
    return page.text


def create_chrome_driver():
    driver_chrome = webdriver.Chrome("chromedriver.exe") #đưa đường dẫn tới file chromedriver.exe vào
    return driver_chrome

def get_number_of_pages (string):
    i = 0
    while(string[i] != 'f'):
        i+=1
    numpage = int(string [i+2:])
    return numpage

def get_comments_from_page(driver, product_id):
    found_comments = []
    found_scores = []
    found_customer_name = []

    base_url = 'https://www.yelp.com{}'
    url = base_url.format(product_id)

    driver.get(url)
    url = driver.current_url+'?osq=Restaurants%3Fstart%3D120&start='
    print(f"Final url:  {driver.current_url}")
    print('\n')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #do web này không thể tìm trang tiếp theo nên phải tìm số lượng trang trước
    numpage = soup.find_all('div', {'class':'lemon--div__373c0__1mboc border-color--default__373c0__3-ifU text-align--center__373c0__2n2yQ'})
    #print(numpage[0].span.text)
    numpage = str(numpage[0].span.text)
    numpage = get_number_of_pages(numpage)
    #print(numpage)


    # get the comments area
    for num in range(numpage):
        num_of_reviews = 0
        index = num*20 #mỗi page sẽ có 20 reviews và link theo đổi theo quy luật là 0, 20, 40, 60,...
        #https://www.yelp.com/biz/shin-toe-bul-yi-san-francisco?osq=Restaurants?osq=Restaurants%3Fstart%3D120&start=540
        #https://www.yelp.com/biz/shin-toe-bul-yi-san-francisco?osq=Restaurants?osq=Restaurants%3Fstart%3D120&start=560
        #print(num)
        #print(f'index: {index}')
        print(f'Page {num}')
        restaurant_url = url + str(index)
        print('Getting reviews from: {}'.format(restaurant_url))
        driver.get(restaurant_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        comment_areas = soup.find_all('div', {'class': 'lemon--div__373c0__1mboc margin-b6__373c0__2Azj6 border-color--default__373c0__3-ifU'})
        if len(comment_areas) == 0:
            print('something went wrong, cannot find review_part')
            return found_comments, found_scores, found_customer_name
    
        # get all comments in review_part
        comment_parts = comment_areas[0].findChildren('li', {'class': 'lemon--li__373c0__1r9wz margin-b3__373c0__q1DuY padding-b3__373c0__342DA border--bottom__373c0__3qNtD border-color--default__373c0__3-ifU'})
        
        if len(comment_parts) is None:
                print('something went wrong, comment_texts is null')
                return found_comments, found_scores, found_customer_name

        for comment_part in comment_parts:
            #get customer's name
            customer_name = comment_part.findChildren('div', {'class': 'lemon--div__373c0__1mboc user-passport-info border-color--default__373c0__3-ifU'})
            if customer_name[0].span.a is not None:
                print(f'Customer name: {customer_name[0].span.a.text}')
                found_customer_name.append(customer_name[0].span.a.text)
            else:
                print("This review doesn't have customer name")
                found_customer_name.append('no name')

                
            # get score
            comment_scores = comment_part.findChildren('span', {'class': 'lemon--span__373c0__3997G display--inline__373c0__3JqBP border-color--default__373c0__3-ifU'})
            comment_scores = str(comment_scores)
            comment_scores = int(comment_scores[124])
            print (f'Star-rating:{comment_scores}')
            found_scores.append(comment_scores)

            # get comment
            comment_texts = comment_part.findChildren('p', {'class': 'lemon--p__373c0__3Qnnj text__373c0__2Kxyz comment__373c0__3EKjH text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa-'})
            print(f"Review: {comment_texts[0].span.text[:50] + '...'}")
            found_comments.append(comment_texts[0].span.text)
            print('\n')

        print('---------------------')
        
        time.sleep(0.4) # delay chương trình 0.6s để tránh bị chặn
    return found_comments, found_scores, found_customer_name 
    

products_filename = 'D:\\YELP\\product_yelp.csv' 
comments_filename = 'D:\\YELP\\comments\\comment_{}.csv'

if __name__ == "__main__":
    df = pandas.read_csv(products_filename, encoding='unicode_escape')
    driver = create_chrome_driver()

    for i in range(len(df)):
        restaurant_name = df.iloc[i, 1].replace(".", "")
        product_id = df.iloc[i, 0]
        print('\n\n_____ Restaurant: {}, {}/{} ___'.format(restaurant_name, i+1, len(df)))
        real_comments_filename = comments_filename.format(restaurant_name)

        print(real_comments_filename)
        print("=========")

        if (os.path.exists(real_comments_filename)):
            print("This restaurant's reviews has been collected already, skip!")
        else:
            #write file
            comments, scores, names = get_comments_from_page(driver, product_id)
            content_str = ''
            for name, score, comment in zip(names, scores, comments):
                content_str += '{},{},{}\n'.format(name, score, comment.replace(',', ' '))
            with open(real_comments_filename, "w", encoding='utf-8') as f:
                f.write('name,score,comment\n' + content_str)

            # output for debug
            print('This restaurant has {} reviews'.format(len(comments)))

    driver.close()
    print('Done')
