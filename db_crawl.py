#한국고전종합DB 크롤러
#해당 사이트는 웹페이지 주소가 ~ITKC_BT_1370A_0020_000_0010&viewSync=OT 형식으로 이루어져 있다.
#각각 책 제목, 각 책이 여러권으로 이루어져있는 경우 해당 권의 제목, 챕터 이름, 페이지를 나타내는 숫자이다.
#이를 book_name, book_number, chap_number, page_num 4개의 변수로 분할하여 웹페이지를 탐색한다.
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json

driver = webdriver.Chrome()
book_name = '1370'
book_number = '0020'
chap_number = '000'
page_num = '0010'
last_fail = False

if not os.path.exists("kor_output"):
    os.makedirs("kor_output")
if not os.path.exists("chn_output"):
    os.makedirs("chn_output")
while (int(book_number)<=280):
    str(book_number).zfill(4)
    try:
        url = f"https://db.itkc.or.kr/dir/item?itemId=BT#dir/node?grpId=&itemId=BT&gubun=book&depth=4&cate1=H&cate2=&dataGubun=%EC%B5%9C%EC%A2%85%EC%A0%95%EB%B3%B4&dataId=ITKC_BT_{book_name}A_{book_number}_{chap_number}_{page_num}&viewSync=OT"
        driver.get(url)
        time.sleep(0.1)
        # XPath를 사용하여 원하는 데이터 추출
        data_kor = driver.find_element(By.XPATH, '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[1]/div/div[3]').text
        data_chn = driver.find_element(By.XPATH, '/html/body/div[2]/section[2]/section[2]/section/div[2]/div[2]/div/div/div[3]').text
        kor_filename = f"kor_output/kor_{book_name}_{book_number}_{chap_number}_{page_num}.json"
        chn_filename = f"chn_output/chn_{book_name}_{book_number}_{chap_number}_{page_num}.json"

        with open(kor_filename, 'w', encoding='utf-8') as output_file_kor:
            json.dump({"data": data_kor}, output_file_kor, ensure_ascii=False)

        with open(chn_filename, 'w', encoding='utf-8') as output_file_chn:
            json.dump({"data": data_chn}, output_file_chn, ensure_ascii=False)

        print(f"데이터가 {kor_filename} 및 {chn_filename} 파일에 저장되었습니다.")
        last_fail = False
        page_num = str(int(page_num) + 10).zfill(4)

    except Exception as e:
        if last_fail == False:
            # page_num, chap_number 값을 조정하여 재시도
            page_num = '0010'
            chap_number = str(int(chap_number) + 10).zfill(3)
            last_fail = True
        else:
            # page_num, chap_number, book_number 값을 모두 조정하여 재시도
            page_num = '0010'
            chap_number = '000'
            book_number = str(int(book_number) + 10).zfill(4)
