from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import csv
import os
# cào comment của 3 loại sản phẩm công nghệ: máy tính bảng, điện thoại và laptop

def writeCSV(filename, star, comment):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for x, y in zip(star, comment):
            writer.writerow([x, y])


def getComment(comment_parts, star, comment):
    for i in range(len(comment_parts)):
        count = 0
        tmp = comment_parts[i].findChildren('i')
        comment.append(tmp[len(tmp) - 1].text)
        for j in range(len(tmp) - 1):
            sao = re.findall(r'iconcom-txtstar', str(tmp[j]))
            if(len(sao) == 1):
                count = count + 1
        star.append(count)


def readCSV(filename, id):
    with open(filename, 'r', encoding='utf-8') as file:
        writer = csv.reader(file)
        for row in writer:
           id.append(row[0])


driver_chrome = webdriver.Chrome("D:\\flask\\data\\chromedriver.exe")

url = 'https://www.thegioididong.com/{}/{}/danh-gia'
filename = '.\\data1\\{}.csv'

products = ['dtdd', 'laptop', 'may-tinh-bang']
id = []
write = 'D:\\flask\\data1\\comment\\comment_{}.csv'
star = []
comment = []
count = 0
for product in products:
    readCSV(filename.format(product), id)
    #print(id)
    for j in id:
        if (os.path.exists(write.format(j))):
            print('This product has been collected already, skip!')
        else:
            driver_chrome.get(url.format(product, j))
            soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')
#       Check next page i
            buttonNext = soup.find_all('div', {'class': 'pgrc'})
            if len(buttonNext) == 0:
                buttonNext.append('000')
            print(j)
            nPage = 1
            numberOfButton = []
            if len(str(buttonNext[0])) > len('[<div class="pgrc"></div>]'):
                numberOfButton = buttonNext[0].findChildren('a')
                nPage = int(numberOfButton[len(numberOfButton) - 2].text)
            pageNumber = 1
            while pageNumber <= nPage:
                soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')
                comment_areas = soup.find_all('ul', {'class': 'ratingLst'})
                if len(comment_areas) == 1:
                    comment_parts = comment_areas[0].findChildren('div', {'class': 'rc'})
                    getComment(comment_parts, star, comment)
                    writeCSV(write.format(j), star, comment)
                else:
                    writeCSV(write.format(j), [''], [''])
#           Click next page
                if pageNumber < nPage:
                    soup = BeautifulSoup(driver_chrome.page_source, 'html.parser')
                    buttonNext = soup.find_all('div', {'class': 'pgrc'})
                    driver_chrome.execute_script("window.scrollTo(0, 7000)") #comment của TGDD chỉ xuất hiện khi kéo xuống, nên method này để kéo xuống
                    driver_chrome.find_element_by_link_text('{}'.format(pageNumber + 1)).click()
                print('Page: {}/{}'.format(pageNumber, nPage))
                pageNumber = pageNumber + 1
                time.sleep(0.7) # phải có method này thì mới scroll được
#       Count comment
            count = count + len(comment)
            #reset lại tất cả danh mục thành rỗng để bắt đầu sang mục mới 
            id = []
            star = []
            comment = []

print('Collect {} comments'.format(count))