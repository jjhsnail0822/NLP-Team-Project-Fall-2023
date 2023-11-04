import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests

driver = webdriver.Chrome()
book_name = '0000'
book_number = '0010'
chap_number = '000'
page_num = '0010'
page_trial = False
chap_trial = False
depth = 4
depth_trial = False
last_trial = False
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

data_of_a_book = {'chn': [], 'kor': []}

while (int(book_name) < 2000):
    str(book_number).zfill(4)
    try:
        url = f"https://db.itkc.or.kr/dir/item?itemId=BT#dir/node?grpId=&itemId=BT&gubun=book&depth={depth}&cate1=Z&cate2=&dataGubun=%EC%B5%9C%EC%A2%85%EC%A0%95%EB%B3%B4&dataId=ITKC_BT_{book_name}A_{book_number}_{chap_number}_{page_num}&viewSync=OT"
        driver.get(url)
        response = None
        while response == None:
            response = requests.get(url)
            time.sleep(0.1)
        # XPath를 사용하여 원하는 데이터 추출
        data_kor = driver.find_element(By.XPATH,
                                       '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[1]/div/div[3]').text
        data_chn = driver.find_element(By.XPATH,
                                       '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[2]/div/div/div[3]').text

        # append data to the dictionary
        data_of_a_book['chn'].append(data_chn)
        data_of_a_book['kor'].append(data_kor)

        page_num = str(int(page_num) + 10).zfill(4)
        page_trial = False
        chap_trial = False
        depth_trial = False
        depth = 4
        last_trial = False
    except Exception as e:
        if depth_trial == False:
            depth = 5
            depth_trial = True
        elif page_trial == False:
            # page_num, chap_number 값을 조정하여 재시도
            page_num = '0010'
            chap_number = str(int(chap_number) + 10).zfill(3)
            page_trial = True
            depth = 4
            depth_trial = False
        elif page_trial == True and chap_trial == False:
            # page_num, chap_number, book_number 값을 모두 조정하여 재시도
            page_num = '0010'
            chap_number = '000'
            book_number = str(int(book_number) + 10).zfill(4)
            chap_trial = True
            depth = 4
            depth_trial = False
        elif last_trial == False:
            chap_number = str(int(chap_number) + 10).zfill(3)
            last_trial = True
            depth = 4
            depth_trial = False
        else:
            # save the data
            if len(data_of_a_book['chn']) == 0:
                print(f"{book_name}에 데이터가 없습니다.")
            else:
                with open(os.path.join(output_folder, f"{book_name}.json"), 'w', encoding='utf-8') as output_file:
                    json.dump(data_of_a_book, output_file, ensure_ascii=False)
                print(f"데이터가 {book_name} 파일에 저장되었습니다.")
                driver.quit()
                driver = webdriver.Chrome() # flush the driver

            # new book
            data_of_a_book = {'chn': [], 'kor': []}
            page_num = '0010'
            chap_number = '000'
            book_number = '0010'
            book_name = int(book_name) + 1
            if book_name == 661:
                book_name = 1288
            book_name = str(book_name).zfill(4)
            depth = 4
